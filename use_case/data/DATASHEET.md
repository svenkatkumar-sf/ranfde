# Datasheet

<!-- Written in TC2, alongside your synthetic data. This file is committed; the
     data itself is not. -->

## What this data is

**Generated on:** 2026-10-20
**Generated from:** 5 hand-written golden examples (CSM scenarios: cadence email, maintenance window, POC handoff, BVS/renewal prep, meeting follow-up). No real records used.
**Rows:** 300 (324 generated → 300 distinct at Jaccard 0.7 threshold → 300 schema-valid)

## Variation axes

<!-- What you varied to get coverage: persona, format, difficulty, edge cases. -->

| Axis | Values |
| --- | --- |
| engagement_level | High (attends every call, expansion-focused) · Moderate (attends some calls) · Low (rarely attends, reactive only) |
| technical_maturity | Fully automated (scripted SDLC, specialized team) · Partially automated (manual steps between automated) · Manual (no automation, no documentation) |
| renewal_proximity | This quarter · Next 6 months · This year · Beyond this year |
| decline | Personal/entertainment question · Non-account conversation · Security/compliance breach request |

## What it can validate

That the assistant responds strictly to account-related queries: renewal status, cadence prep, platform health, and next best actions tied to a specific account. That it declines questions outside account scope — personal questions, non-account conversations, and requests that would violate security or compliance. That responses stay focused on the account in question and recommend a clear next step.

## What it cannot validate

Whether the assistant performs correctly with real account context — actual Org62 data, real calendar entries, live renewal dates, or CRM history. The synthetic inputs are clean, well-formed questions; real CSM inputs include Salesforce shorthand, partial context, and account history that this data does not carry. It also cannot validate cross-account reasoning: each account is unique and needs its own context, and this data was generated one account at a time with no shared state between rows.

## What it must never be compared against

Real Org62 account records, real calendar or renewal data, or any eval set built from actual CSM interactions. A score on this synthetic set is not a proxy for performance on live accounts. The two measure different things.

## Leakage check — outward (what left)

- [x] No real record was used as a seed.
- [x] No real entity names, IDs, or identifiers appear. *(1 flag: "Agent Fabric POC" — a made-up project name from golden example that appeared in 1 generated row. No real company or customer identifiers.)*
- [x] No distinctive internal formats that would identify the firm.
- [x] Rare categories were generated, not copied.

## Leakage check — inward (what the eval shares with the training data)

**Are the goldens disjoint from anything the system was, or will be, tuned on?**
Yes, disjoint. The system prompt and golden examples are hand-written; no fine-tuning has been done.

**Overlap between `golden.jsonl` and this file, by the dedupe measure:** 0 rows at Jaccard threshold 0.7 (seeds were used as generation prompts only, not included in output)
