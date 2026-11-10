# Decision log

One row per architectural decision, with the option you rejected and why.

> **Week 5 asks you to defend your agent architecture against the alternatives.**
> **Week 10's handoff doc is largely this file.** Both are much easier if you
> wrote the reasoning down while you still remembered it.

A decision without a rejected alternative is not a decision, it is a default.
If you cannot name what you did not do, you did not choose.

| Week | Decision | What you rejected | Why | What would change your mind |
| --- | --- | --- | --- | --- |
| 1 | Pipeline: user pastes account context manually, single LLM call returns prioritized actions | Full agent that autonomously fetches data from OrgCS / Org62 / Gmail | No live integrations exist yet; validating the core use case end-to-end first is more valuable than building integrations before the output is trusted | Each integration added (OrgCS → Org62 → Gmail → Admin APIs) makes one pipeline step autonomous — the design is modular so features ship in releases without a rewrite |
| 2 | Reframe infra/ops scenarios as escalation recommendations, not CSM-owned actions | Keeping generated rows where assistant suggests CSM initiates technical changes | Fellow CSM review confirmed CSMs don't own platform configs or logs — those are ops/customer territory; direct-action responses are unrealistic and would lose trust immediately | If the app ever integrates with ops ticketing systems, CSM-triggered escalation workflows become the correct pattern |
| 3 | Hybrid RRF (BM25 + dense cosine, top-5, text-embedding-3-small) | BM25 alone (38% pass, 12% full-citation); Dense alone (62% pass, 25% full-citation) | Hybrid doubled full-citation rate vs Dense (50% vs 25%) on the same pass rate — critical because 4 of 10 eval questions require two records; BM25 alone missed paraphrase queries entirely. Demo feedback confirmed the priority is functional accuracy over presentation: responses must feel operationally grounded, which requires real production data (OrgCS, Org62) replacing the synthetic corpus | Switch to Dense-only if a stronger embedding model pushes full-citation above 40% — simpler code, lower latency, no BM25 index to maintain. Switch corpus to production data when data-governance approval is obtained |
| 5 — Session 9 questions | **Two to fix:** (1) Sources not visible enough — Phil noted CSMs cannot see where each answer came from; citations must appear clearly before the portal is used in customer conversations. (2) Eval examples lack measurable inputs and expected outputs — Tyler flagged that test cases need concrete, scoreable pairs not open-ended prompts. **One open:** Can CSMs validate the top-3 ranked actions against real data before expanding the pilot? Requires real corpus and a CSM review session — not resolved yet. | <!-- --> | <!-- --> | <!-- --> |
| 5 | Direct Gradio API call — user invokes solve() from the UI, one LLM call inside | Tool-call loop — model decides when to call solve(), formulates final answer in a second turn | Direct wins on every measured dimension: 1 model call vs 2, ~250 tokens vs ~2,000, ~10s vs ~20s latency. The tool result (1,194 bytes / ~269 tokens) re-enters context on every call, making the tool loop ~8× more expensive at this response size. Capability calls are identical — solve() runs once either way. No external caller exists today that needs to discover solve() autonomously | Switch to tool loop when an orchestrating agent needs to choose between multiple capabilities (e.g. solve(), get_cases(), check_renewal()) — at that point the model's ability to select the right tool outweighs the token cost. Not yet: the user drives that decision in the UI |
| 6 | <!-- guardrail level --> | <!-- --> | <!-- --> | <!-- --> |
| 7 | <!-- memory type --> | <!-- --> | <!-- --> | <!-- --> |
| 8 | <!-- model --> | <!-- --> | <!-- --> | <!-- --> |

---

The last column is the one people skip and the one people ask about. "We chose
dense retrieval; we would switch to hybrid if exact-match queries went above ~20%
of traffic" is an engineering position. "We chose dense retrieval" is a
preference.
