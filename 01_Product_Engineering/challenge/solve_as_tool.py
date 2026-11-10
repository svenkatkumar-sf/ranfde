"""Second implementation: solve() exposed as a LiteLLM function tool.

The model decides when to call solve() and formulates the final answer.
Contrast with the direct Gradio API path where the user drives the invocation.

Model calls:  2 minimum (decide → call → answer)
Cap calls:    1 (solve() still runs once)
Token cost:   grows with response size — the tool result re-enters context
"""

import json
import os
import time
from pathlib import Path

import litellm
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")

MODEL      = os.getenv("LLM_MODEL", "gpt-4.1-mini")
API_BASE   = os.getenv("LLM_API_BASE") or os.getenv("AZURE_API_BASE")
API_KEY    = os.getenv("AZURE_API_KEY")
API_VERSION = os.getenv("AZURE_API_VERSION")

SOLVE_TOOL = {
    "type": "function",
    "function": {
        "name": "solve",
        "description": (
            "Retrieve account records and return prioritized next actions with sources. "
            "Given a Salesforce account name and plain-text context, retrieves the most "
            "relevant records from the CSM knowledge base and returns 3-5 prioritized "
            "next actions grounded in those records. Every answer names the records it "
            "came from. Returns a JSON string matching the Response schema."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "account_name": {
                    "type": "string",
                    "description": "Salesforce account name, e.g. NovaTech, OrionSystems",
                },
                "context": {
                    "type": "string",
                    "description": "Free-text context — meeting notes, question, health signals",
                },
            },
            "required": ["account_name", "context"],
        },
    },
}


def _llm(**kwargs) -> litellm.ModelResponse:
    kw = {"model": MODEL, **kwargs}
    if API_BASE:    kw["api_base"]    = API_BASE
    if API_KEY:     kw["api_key"]     = API_KEY
    if API_VERSION: kw["api_version"] = API_VERSION
    return litellm.completion(**kw)


def solve_via_tool(account_name: str, context: str) -> dict:
    """Run solve() as a model-driven tool call. Returns answer + metrics.

    Returns:
        {
          "answer":           str,
          "model_calls":      int,   # LLM round trips
          "capability_calls": int,   # times solve() actually ran
          "tokens":           int,   # total tokens across all turns
          "latency":          float, # wall-clock seconds
        }
    """
    from app import solve  # imported here so the module loads its corpus once

    model_calls = 0
    capability_calls = 0
    tokens = 0
    t0 = time.perf_counter()

    messages = [
        {
            "role": "system",
            "content": (
                "You are Maxi, a CSM assistant. "
                "Use the solve tool to answer questions about accounts."
            ),
        },
        {
            "role": "user",
            "content": f"Account: {account_name}\n\nQuestion: {context}",
        },
    ]

    # Turn 1 — model decides to use the tool
    model_calls += 1
    r1 = _llm(messages=messages, tools=[SOLVE_TOOL], tool_choice="auto")
    tokens += r1.usage.total_tokens
    msg1 = r1.choices[0].message

    # Append assistant turn (handles both tool-call and plain-text responses)
    assistant_turn = {"role": "assistant", "content": msg1.content or ""}
    if msg1.tool_calls:
        assistant_turn["tool_calls"] = [
            tc.model_dump() if hasattr(tc, "model_dump") else tc
            for tc in msg1.tool_calls
        ]
    messages.append(assistant_turn)

    answer = msg1.content or ""

    if msg1.tool_calls:
        for tc in msg1.tool_calls:
            if tc.function.name == "solve":
                capability_calls += 1
                args = json.loads(tc.function.arguments)
                result = solve(
                    args.get("account_name", account_name),
                    args.get("context", context),
                )
                messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": result}
                )

        # Turn 2 — model formulates the final answer from tool result
        model_calls += 1
        r2 = _llm(messages=messages)
        tokens += r2.usage.total_tokens
        answer = r2.choices[0].message.content or ""

    return {
        "answer": answer,
        "model_calls": model_calls,
        "capability_calls": capability_calls,
        "tokens": tokens,
        "latency": time.perf_counter() - t0,
    }
