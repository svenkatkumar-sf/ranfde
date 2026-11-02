import json
import time
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
import litellm

REPO = Path(__file__).parent.parent.parent
CORPUS_PATH = REPO / "use_case" / "data" / "synthetic_v1.jsonl"
EVALS_PATH = REPO / "use_case" / "evals" / "retrieval.jsonl"
EMB_CACHE = Path(__file__).parent / ".corpus_embeddings.npy"

load_dotenv(REPO / ".env")

TOP_K = 5

# ── Load ──────────────────────────────────────────────────────────────

rows = [json.loads(l) for l in CORPUS_PATH.read_text().splitlines() if l.strip()]
questions = [json.loads(l) for l in EVALS_PATH.read_text().splitlines() if l.strip()]
texts = [r["input"] for r in rows]

# ── BM25 index ────────────────────────────────────────────────────────

bm25 = BM25Okapi([t.lower().split() for t in texts])

# ── Embeddings ────────────────────────────────────────────────────────

def _embed(input_texts: list[str]) -> np.ndarray:
    model = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    api_base = os.getenv("EMBED_API_BASE") or os.getenv("AZURE_API_BASE")
    api_key = os.getenv("EMBED_API_KEY") or os.getenv("AZURE_API_KEY")
    api_version = os.getenv("EMBED_API_VERSION", "2025-04-01-preview")
    # LiteLLM requires "azure/<deployment-name>" for Azure endpoints
    full_model = f"azure/{model}" if api_base and "azure" in api_base else model
    resp = litellm.embedding(
        model=full_model,
        input=input_texts,
        api_base=api_base,
        api_key=api_key,
        api_version=api_version,
    )
    return np.array([d["embedding"] for d in resp.data], dtype=np.float32)


def load_corpus_embeddings() -> np.ndarray:
    if EMB_CACHE.exists():
        print(f"  Loading cached embeddings from {EMB_CACHE.name}")
        return np.load(EMB_CACHE)
    print(f"  Embedding {len(texts)} rows (first run only — will cache)...")
    # Batch in chunks of 100 to stay under Azure's per-request limit
    all_vecs = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        all_vecs.append(_embed(batch))
        print(f"    {min(i + batch_size, len(texts))}/{len(texts)}")
    emb = np.concatenate(all_vecs, axis=0)
    np.save(EMB_CACHE, emb)
    print(f"  Saved to {EMB_CACHE.name}")
    return emb


def cosine_ranked(query_vec: np.ndarray, corpus_vecs: np.ndarray) -> list[int]:
    """Return all corpus indices sorted best-first by cosine similarity."""
    q = query_vec / (np.linalg.norm(query_vec) + 1e-9)
    c = corpus_vecs / (np.linalg.norm(corpus_vecs, axis=1, keepdims=True) + 1e-9)
    sims = c @ q
    return sims.argsort()[::-1].tolist()


def cosine_top_k(query_vec: np.ndarray, corpus_vecs: np.ndarray) -> list[int]:
    return cosine_ranked(query_vec, corpus_vecs)[:TOP_K]


def rrf_fuse(rank_lists: list[list[int]], k: int = 60) -> list[int]:
    scores: dict[int, float] = {}
    for ranks in rank_lists:
        for rank, idx in enumerate(ranks):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=lambda i: -scores[i])[:TOP_K]

# ── Retrieve ──────────────────────────────────────────────────────────

def retrieve_bm25(question: str) -> dict:
    t0 = time.perf_counter()
    idx = bm25.get_scores(question.lower().split()).argsort()[-TOP_K:][::-1].tolist()
    return {
        "sources": [str(i) for i in idx],
        "calls": 0,
        "evidence_chars": sum(len(texts[i]) for i in idx),
        "latency": time.perf_counter() - t0,
        "stopped_by": "top_k",
    }


def retrieve_dense(question: str, corpus_vecs: np.ndarray) -> dict:
    t0 = time.perf_counter()
    q_vec = _embed([question])[0]
    idx = cosine_top_k(q_vec, corpus_vecs)
    return {
        "sources": [str(i) for i in idx],
        "calls": 1,
        "evidence_chars": sum(len(texts[i]) for i in idx),
        "latency": time.perf_counter() - t0,
        "stopped_by": "top_k",
    }


def retrieve_hybrid(question: str, corpus_vecs: np.ndarray) -> dict:
    t0 = time.perf_counter()
    bm25_order = bm25.get_scores(question.lower().split()).argsort()[::-1].tolist()
    q_vec = _embed([question])[0]
    dense_order = cosine_ranked(q_vec, corpus_vecs)
    idx = rrf_fuse([bm25_order, dense_order])
    return {
        "sources": [str(i) for i in idx],
        "calls": 1,
        "evidence_chars": sum(len(texts[i]) for i in idx),
        "latency": time.perf_counter() - t0,
        "stopped_by": "top_k (rrf)",
    }

# ── Score ─────────────────────────────────────────────────────────────

def score(result: dict, gold: list[str]) -> dict:
    """pass = at least one gold id retrieved; cited_all = every gold id retrieved"""
    if not gold:
        return {"pass": None, "cited_all": None}  # decline question, scored separately
    sources = set(result["sources"])
    return {
        "pass": any(g in sources for g in gold),
        "cited_all": all(g in sources for g in gold),
    }

# ── Main ──────────────────────────────────────────────────────────────

def run() -> None:
    print(f"\nCorpus: {len(rows)} rows | Questions: {len(questions)}")

    corpus_vecs = load_corpus_embeddings()

    techniques = {
        "BM25":         lambda q: retrieve_bm25(q),
        "Dense":        lambda q: retrieve_dense(q, corpus_vecs),
        "Hybrid (RRF)": lambda q: retrieve_hybrid(q, corpus_vecs),
    }

    COL = 15
    header = (
        f"{'Technique':<{COL}} {'Pass':>6} {'Cited':>6} "
        f"{'Calls':>6} {'Evid(ch)':>9} {'Latency':>9}  Stopped"
    )
    bar = "─" * len(header)

    print(f"\n{bar}\n{header}\n{bar}")

    for name, fn in techniques.items():
        passes = citations = calls_total = evidence_total = n_scored = 0
        latency_total = 0.0

        for q in questions:
            result = fn(q["question"])
            s = score(result, q["gold"])
            calls_total += result["calls"]
            evidence_total += result["evidence_chars"]
            latency_total += result["latency"]
            if s["pass"] is not None:
                n_scored += 1
                if s["pass"]:      passes += 1
                if s["cited_all"]: citations += 1

        n = len(questions)
        print(
            f"{name:<{COL}} {passes/n_scored:>5.0%}  {citations/n_scored:>5.0%}  "
            f"{calls_total:>6}  {evidence_total/n:>9,.0f}  {latency_total/n:>7.3f}s  "
            f"{result['stopped_by']}"
        )

    print(bar)
    model = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    print(f"\nSettings: embed_model={model}, top_k={TOP_K}, corpus={len(rows)} rows")
    n_decline = sum(1 for q in questions if not q["gold"])
    n_scoreable = len(questions) - n_decline
    print(f"Pass/Cited rates over {n_scoreable} scoreable questions ({n_decline} decline questions excluded)")
    estimated_tokens = len(texts) * 200
    print(f"Embedding tokens (corpus, first run): ~{estimated_tokens:,} estimated — check litellm debug for measured count")


if __name__ == "__main__":
    run()
