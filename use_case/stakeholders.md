# Stakeholders

Everyone you talk to about this project, from the first "where would this even
run?" to the final readout.

> **Week 10's technical challenge is a report to the people in this file.**
> You cannot write it later from memory. Add a row the day you have the
> conversation.

Use roles, not names. This is a public repo.

| Week | Who (role) | What you asked | What you learned | Follow-up |
| --- | --- | --- | --- | --- |
| 1 | Director, Customer Success | Where would a containerized internal app run? Who would use it? | EKS on AWS; Okta auth; Azure OpenAI is already whitelisted; realized building a real product for the team is achievable | Confirm internal container registry and secrets management with platform team |
| 2 | Fellow CSM | Showed 20 synthetic rows: which would never happen? What's missing? Would anything worry you if this were public? | CSMs don't have access to operational logs or platform configs — those are ops/customer territory. Technical next-step suggestions were right in intent but wrong in execution — CSMs can't make infra changes unilaterally; they escalate. Competitive analysis and marketing campaign assistance are valid CSM activities — the assistant over-declined those. Tone needs to be warmer and more account-specific since CSMs manage multiple accounts. | Regenerate with reframed infra scenarios (escalation, not direct action); revisit decline rules for competitive research and marketing support. |
| 3 | Fellow CSM | Observed live demo of Maxi — account action prioritizer answering cadence and renewal questions with sources | Asked why the answers, although relevant, don't feel like how we'd really operate. Explained responses are retrieved from synthetic data, not live account records — the gap is the corpus, not the retrieval. Confirmed that with real OrgCS/Org62 data the operational grounding would improve significantly | Replace synthetic corpus with real account data exports as the next milestone |
| 3 | Director, Customer Success | Showed Maxi The SuccessWeaver — account action prioritizer with hybrid retrieval over synthetic CSM data. Asked: would you act on these answers? Does the source convince you? What would you want to ask that you didn't? | Do not over-invest in UI and dashboards — Claude itself is a capable agent. The priority is properly assembled data; good data will unlock the real value of the service. Response quality looks promising. | Identify which production data sources (OrgCS, Org62, case exports) would replace the synthetic corpus and what data-governance approvals are needed before indexing them. |

| 5 | Director, Customer Success | Live demo of Maxi containerized (Docker) with hybrid retrieval and solve endpoint. Five questions from stakeholder after the run. | (1) **Real data timeline** — first question was when can this connect to real data; synthetic corpus is visibly a gap to an operational audience. (2) **Source transparency** — no indication in the UI of which data sources are being queried; stakeholder couldn't tell whether it was reading cases, account records, or calendar. (3) **CSM behavior customization** — asked whether individual CSMs can adjust what the assistant prioritizes. (4) **Manager enforcement layer** — Director wants to push dates and action items to CSMs from above, not just surface them; the current model is pull-only. (5) **Persistent context + Google Drive sync** — wants context stored locally and mirrored to Google Drive so the app can be re-run at any time with the latest state. (6) **Scheduled execution** — asked whether the app can run periodically instead of on user trigger; frequency would depend on data source change rate. (7) **Email integration** — asked whether outputs could be routed to email. | (1) Map each action card back to its source system in the UI (OrgCS / Org62 / Calendar). (2) Design a manager-facing config layer for enforcing dates and action items. (3) Evaluate scheduled corpus refresh cadence once real data sources are connected. (4) Email routing and Google Drive sync are post-pilot scope — note for Week 9 deployment planning. |

---

## Not everyone is an infrastructure contact

The useful list is wider than it first looks, and Week 10's report goes to all of
them:

- **The person with the problem** — the one from your charter. Have you shown
  them anything yet?
- **Whoever owns the data** you would need.
- **Whoever runs the platform** your app would deploy onto.
- **Whoever approves** a deployment, a spend, or a vendor.
- **Your own manager**, who will be asked whether this was worth the ten weeks.

If a week goes by with no conversation, add a row saying so and why. A visible
gap is more useful than a silent one.
