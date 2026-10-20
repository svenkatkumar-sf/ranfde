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
| 3 | <!-- retrieval approach --> | <!-- --> | <!-- --> | <!-- --> |
| 5 | <!-- agent architecture --> | <!-- --> | <!-- --> | <!-- --> |
| 6 | <!-- guardrail level --> | <!-- --> | <!-- --> | <!-- --> |
| 7 | <!-- memory type --> | <!-- --> | <!-- --> | <!-- --> |
| 8 | <!-- model --> | <!-- --> | <!-- --> | <!-- --> |

---

The last column is the one people skip and the one people ask about. "We chose
dense retrieval; we would switch to hybrid if exact-match queries went above ~20%
of traffic" is an engineering position. "We chose dense retrieval" is a
preference.
