"""TC5 Step 4+5: Measure direct Gradio API call vs tool-call loop.

Runs both implementations on the same two requests and prints:
  model calls | capability calls | latency | tokens | response bytes

Step 5: real response size — how many bytes solve() actually returns,
and what that means for the tool loop's token bill.
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

import litellm
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from app import solve
from solve_as_tool import solve_via_tool, MODEL, API_BASE, API_KEY, API_VERSION

# ── Two test requests ──────────────────────────────────────────────────────────

REQUESTS = [
    (
        "NovaTech",
        "I have a cadence call this Thursday. What should I focus on and what do I need to prepare?",
    ),
    (
        "OrionTech",
        "What should I prioritize ahead of their renewal this quarter?",
    ),
]

# ── Direct measurement ─────────────────────────────────────────────────────────

def measure_direct(account_name: str, context: str) -> dict:
    """Direct path: user calls solve() via Gradio API, one LLM call inside."""
    t0 = time.perf_counter()
    result = solve(account_name, context)
    latency = time.perf_counter() - t0
    # Estimate tokens for the inner LLM call only (no outer loop)
    inner_tokens = litellm.token_counter(
        model=MODEL,
        messages=[{"role": "user", "content": result}],
    )
    return {
        "model_calls": 1,
        "capability_calls": 1,
        "tokens": f"~{inner_tokens} (inner only)",
        "latency": latency,
        "response_bytes": len(result.encode()),
        "result": result,
    }

# ── Main ───────────────────────────────────────────────────────────────────────

def run() -> None:
    COL = 38
    header = (
        f"{'Request':<{COL}} {'Way':<12} "
        f"{'Model calls':>11} {'Cap calls':>9} "
        f"{'Tokens':>10} {'Latency':>9} {'Bytes':>8}"
    )
    bar = "─" * len(header)

    print(f"\n{bar}\n{header}\n{bar}")

    direct_bytes = None

    for account, context in REQUESTS:
        label = f"{account}: {context[:34]}…"

        # Direct
        d = measure_direct(account, context)
        direct_bytes = d["response_bytes"]
        print(
            f"{label:<{COL}} {'Direct (Gradio)':<12} "
            f"{d['model_calls']:>11} {d['capability_calls']:>9} "
            f"{str(d['tokens']):>10} {d['latency']:>8.2f}s {d['response_bytes']:>8}"
        )

        # Tool loop
        t = solve_via_tool(account, context)
        print(
            f"{'':>{COL}} {'Tool loop':<12} "
            f"{t['model_calls']:>11} {t['capability_calls']:>9} "
            f"{t['tokens']:>10} {t['latency']:>8.2f}s {'—':>8}"
        )
        print()

    print(bar)

    # ── Step 5: real response size ─────────────────────────────────────────────
    print(f"\n── Step 5: real response size ──────────────────────────────────")
    sample = solve("NovaTech", "I have a cadence call this Thursday. What should I focus on?")
    size_bytes = len(sample.encode())
    size_tokens = litellm.token_counter(
        model=MODEL,
        messages=[{"role": "tool", "content": sample, "tool_call_id": "x"}],
    )
    print(f"  solve() response:  {size_bytes} bytes  (measured)")
    print(f"  As tool result:    ~{size_tokens} tokens re-enter context each call")
    print(f"  Direct path:       response consumed once, never re-encoded")
    print(
        f"\n  Finding: tool loop adds ~{size_tokens} tokens/call vs direct "
        f"at this response size ({size_bytes}B). At 2× calls/request that is "
        f"~{size_tokens * 2} extra tokens per user query."
    )
    print(f"\nSettings: model={MODEL}")


if __name__ == "__main__":
    run()
