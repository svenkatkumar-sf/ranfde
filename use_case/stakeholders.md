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
