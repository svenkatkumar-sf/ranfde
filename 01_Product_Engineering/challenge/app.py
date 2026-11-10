"""The server.

`gradio.Server` is a FastAPI app with Gradio's API engine bolted in. You get
queueing, streaming, and MCP for free, but you bring your own frontend. That
split is the point: the API is the product, the UI is disposable.
"""

import os
import json
from pathlib import Path

import numpy as np
import litellm
from fastapi.responses import HTMLResponse
from gradio import Server

from llm import stream_reply

from pydantic import BaseModel
from enum import Enum
from rank_bm25 import BM25Okapi
from helpers.config import from_env
from helpers.llm import chat as llm_chat


app = Server()

FRONTEND = Path(__file__).parent / "frontend" / "index.html"
ROOT = Path(__file__).parent.parent.parent
CORPUS_PATH = ROOT / "use_case" / "data" / "synthetic_v1.jsonl"
EMB_CACHE = Path(__file__).parent / ".corpus_embeddings.npy"

cfg = from_env(ROOT)

# ── Retrieval setup (loaded once at startup) ─────────────────────────

_rows = [json.loads(l) for l in CORPUS_PATH.read_text().splitlines() if l.strip()]
_texts = [r["input"] for r in _rows]
_bm25 = BM25Okapi([t.lower().split() for t in _texts])
if EMB_CACHE.exists():
    _corpus_vecs: np.ndarray = np.load(EMB_CACHE)
else:
    # No cache — build embeddings at startup (one-time API call per deployment)
    import os as _os
    _model = _os.getenv("EMBED_MODEL", "text-embedding-3-small")
    _api_base = _os.getenv("EMBED_API_BASE") or _os.getenv("AZURE_API_BASE")
    _full_model = f"azure/{_model}" if _api_base and "azure" in _api_base else _model
    _emb_resp = litellm.embedding(
        model=_full_model,
        input=_texts,
        api_base=_api_base,
        api_key=_os.getenv("EMBED_API_KEY") or _os.getenv("AZURE_API_KEY"),
        api_version=_os.getenv("EMBED_API_VERSION", "2025-04-01-preview"),
    )
    _corpus_vecs = np.array([d["embedding"] for d in _emb_resp.data], dtype=np.float32)
    np.save(EMB_CACHE, _corpus_vecs)

TOP_K = 5
DECLINE_THRESHOLD = 0.46  # cosine similarity below this → clearly off-domain, skip LLM call


def _embed_query(question: str) -> np.ndarray:
    model = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    api_base = os.getenv("EMBED_API_BASE") or os.getenv("AZURE_API_BASE")
    full_model = f"azure/{model}" if api_base and "azure" in api_base else model
    resp = litellm.embedding(
        model=full_model,
        input=[question],
        api_base=api_base,
        api_key=os.getenv("EMBED_API_KEY") or os.getenv("AZURE_API_KEY"),
        api_version=os.getenv("EMBED_API_VERSION", "2025-04-01-preview"),
    )
    return np.array(resp.data[0]["embedding"], dtype=np.float32)


def _hybrid_retrieve(question: str) -> tuple[list[int], float]:
    """Return (top-k indices, best cosine similarity) using BM25+dense RRF."""
    # BM25 ranking
    bm25_order: list[int] = _bm25.get_scores(question.lower().split()).argsort()[::-1].tolist()

    # Dense ranking + top cosine for decline detection
    q_vec = _embed_query(question)
    c = _corpus_vecs / (np.linalg.norm(_corpus_vecs, axis=1, keepdims=True) + 1e-9)
    q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-9)
    sims = c @ q_norm
    dense_order: list[int] = sims.argsort()[::-1].tolist()
    best_sim = float(sims.max())

    # RRF fusion
    scores: dict[int, float] = {}
    for rank_list in [bm25_order, dense_order]:
        for rank, idx in enumerate(rank_list):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (60 + rank + 1)
    top_k = sorted(scores, key=lambda i: -scores[i])[:TOP_K]
    return top_k, best_sim

# --- The API -----------------------------------------------------------------
# The `-> str` return annotation is REQUIRED. Without it Gradio infers zero
# output components and silently returns nothing. Ask us how we know.


@app.api(name="chat")
def chat(message: str, history: list | None = None) -> str:
    """Answer a free-form question about your accounts, grounded in retrieved records."""
    top_k, best_sim = _hybrid_retrieve(message)
    if best_sim >= DECLINE_THRESHOLD:
        hits = [(i, _rows[i]) for i in top_k]
        ctx = "\n\n".join(f"[Source {i}] {row['input']}\n→ {row['output']}" for i, row in hits)
        system = (
            "You are Maxi, an AI CSM assistant. "
            "Answer using ONLY the retrieved account records below. "
            "If they don't address the question, say so — do not invent information.\n\n"
            f"Retrieved records:\n{ctx}"
        )
    else:
        system = (
            "You are Maxi, an AI CSM assistant. "
            "The question appears to be outside the scope of the account knowledge base — "
            "say so briefly and suggest rephrasing with a specific account name."
        )
    yield from stream_reply(message, history, system=system)

@app.api(name="next_actions")
def next_actions(account_name: str, context: str) -> str:
    """Return prioritized next actions for a CSM account."""
    prompt = f"""You are an expert CSM assistant. Given the following context for account {account_name},
return a prioritized list of 3-5 next best actions ranked by urgency.

For each action include:
- The action to take
- Category (Operations / Cadence / Renewal / Engagement)
- Time horizon (immediate / this week / this month / this quarter)

Context:
{context}

If there is not enough information to suggest actions, say so clearly."""

    yield from stream_reply(prompt)


# --- The frontend ------------------------------------------------------------
# Defining a route at "/" replaces Gradio's default UI with ours.


@app.get("/", response_class=HTMLResponse)
def homepage() -> str:
    return FRONTEND.read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    """Your future ops team will thank you. Load balancers need this."""
    return {"status": "ok", "model": os.getenv("LLM_MODEL", "gpt-4.1-mini")}

class UrgencyLevel(str, Enum):
      IMMEDIATE = "immediate"
      THIS_WEEK = "this week"
      THIS_MONTH = "this month"
      THIS_QUARTER = "this quarter"

class Request(BaseModel):
      account_name: str
      context: str  # meeting notes, open items, renewal date, health signals

class Action(BaseModel):
      action: str
      category: str   # Operations / Cadence / Renewal / etc.
      urgency: UrgencyLevel    # e.g. "3 days", "2 weeks", "3 months"

class Response(BaseModel):
      account_name: str
      sources: list[str] = []
      actions: list[Action]
      message: str | None = None

@app.api(name="solve")
def solve(account_name: str, context: str) -> str:
    """Retrieve account records and return prioritized next actions with sources.

    Given a Salesforce account name and plain-text context (meeting notes, open
    cases, renewal signals), this tool retrieves the most relevant account records
    from the CSM knowledge base using hybrid BM25+dense retrieval, then returns
    3-5 prioritized next actions grounded in those records.

    Args:
        account_name: The Salesforce account name (e.g. "NovaTech", "OrionSystems").
        context: Free-text context — meeting notes, open items, health signals,
                 renewal date, or any question about the account.

    Returns:
        JSON string matching the Response schema:
        {
          "account_name": str,
          "sources": list[str],   # record IDs retrieved; cite these in follow-up
          "actions": [{"action": str, "category": str, "urgency": str}, ...],
          "message": str | null   # set when the corpus cannot answer the question
        }

    Decline behaviour: returns an empty actions list and a message when the
    retrieved records score below the similarity threshold — the corpus does not
    contain an answer rather than fabricating one.
    """
    query = f"{account_name}: {context}"
    top_k, best_sim = _hybrid_retrieve(query)

    if best_sim < DECLINE_THRESHOLD:
        return Response(
            account_name=account_name,
            sources=[],
            actions=[],
            message="No relevant records found in the knowledge base for this question.",
        ).model_dump_json()

    hits = [(i, _rows[i]) for i in top_k]
    retrieved_context = "\n\n".join(
        f"[Source {i}] {row['input']}\n→ {row['output']}" for i, row in hits
    )

    prompt = f"""You are a CSM assistant. A user asked:

"{context}"

The following records were retrieved from the knowledge base:

{retrieved_context}

IMPORTANT: Only answer if these records directly address the question. If they do not — even if they are from the same domain — return ONLY:
{{"decline": true, "message": "<one sentence: what information is missing>"}}

If the records do address the question, return ONLY a JSON array of 3-5 prioritized next actions for {account_name}. No other text.
Format: [{{"action": "...", "category": "Operations|Cadence|Renewal|Engagement", "urgency": "immediate|this week|this month|this quarter"}}]"""

    raw = llm_chat(cfg, prompt).strip().strip("```json").strip("```").strip()
    parsed = json.loads(raw)

    if isinstance(parsed, dict) and parsed.get("decline"):
        return Response(
            account_name=account_name,
            sources=[str(i) for i in top_k],
            actions=[],
            message=parsed.get("message", "The knowledge base does not contain enough information to answer this question."),
        ).model_dump_json()

    actions = [Action(**a) for a in parsed]
    return Response(
        account_name=account_name,
        actions=actions,
        sources=[str(i) for i in top_k],
    ).model_dump_json()
     


if __name__ == "__main__":
    # 0.0.0.0 so the container is reachable from the host. On your laptop this
    # is fine. On a firm network, "reachable from where, exactly?" is the
    # question this challenge wants you to go ask.
    #
    # Read the port rather than hardcoding it, so a machine that already has
    # something on 7860 can move this one without editing code.
    port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    # Gradio announces the address it BOUND to, which is 0.0.0.0 -- not an
    # address a browser can open. Windows rejects it outright; macOS and Linux
    # quietly redirect it to localhost, which is why it looks fine on some
    # machines and broken on others. Print the one that always works.
    print(f"\n  Open http://localhost:{port} in your browser\n", flush=True)
    app.launch(server_name="0.0.0.0", server_port=port)
