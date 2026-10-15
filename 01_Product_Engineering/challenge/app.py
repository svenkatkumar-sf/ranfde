"""The server.

`gradio.Server` is a FastAPI app with Gradio's API engine bolted in. You get
queueing, streaming, and MCP for free, but you bring your own frontend. That
split is the point: the API is the product, the UI is disposable.
"""

import os
from pathlib import Path

from fastapi.responses import HTMLResponse
from gradio import Server

from llm import stream_reply

from pydantic import BaseModel
from enum import Enum

app = Server()

FRONTEND = Path(__file__).parent / "frontend" / "index.html"


# --- The API -----------------------------------------------------------------
# The `-> str` return annotation is REQUIRED. Without it Gradio infers zero
# output components and silently returns nothing. Ask us how we know.


@app.api(name="chat")
def chat(message: str, history: list | None = None) -> str:
    """Stream a reply to one user message."""
    yield from stream_reply(message, history)

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
      actions: list[Action]
      message: str | None = None

def solve(request: Request) -> Response:
    ...


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
