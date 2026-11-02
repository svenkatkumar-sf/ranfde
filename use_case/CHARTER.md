# Project charter

<!--
  Fill this in during TC1 Step 4, from your Getting to Concreteness form.
  Later weeks' notebooks read this file and stop if it is still the template.
  That is on purpose.
-->

**Department:** Customer Success

**Working title:** CSM Account Action Prioritizer

---

## The problem

**Who has it?** One real role, not a department.

Customer Success Manager

**What are they trying to do?**

They need to go to multiple systems to find the next best action and accounts. More than the work itself, Prioritizing and getting to know what needs to be done takes linger

**How do they handle it today?**

Manually switching between Slack, Gmail, OrgCS, Org62 — piecing it together per account. 

**What does that cost — time, money, risk, or relationships?**

Time lost to context-switching across accounts; risk of missing a renewal signal or a promised follow-up

**The problem in one sentence. No solution in it.**

A CSM managing multiple accounts loses hours each week piecing together account context from four separate systems to figure out what needs attention.

---

## Success

**What does the new world look like for that person?**

I focus entirely on customer work — analyzing data, reading accounts, adding value — instead of operational tasks.

**How would the firm measure it? Which numbers should move?**

OpEx reduced, customer engagements increase, adoption grows, expansion revenue goes up.

---

## The first product

**Your solution in one sentence.**

A unified CSM portal that surfaces automated insights from connected systems (Salesforce, Anypoint Admin, Google Calendar, public news) and answers ad-hoc questions via chat — so a CSM spends time on customer work, not on piecing together signals.

**Two interaction modes — both required:**

| Mode | Trigger | What happens |
| --- | --- | --- |
| **Proactive (push)** | Scheduled monitor or system event | Portal surfaces an alert with context and suggested action — S1 raised, vCore declining, QBR date approaching, leadership change detected |
| **Reactive (pull)** | CSM asks a question in chat | Chat retrieves relevant records and returns prioritized next actions with sources |

**Input → Output.** Be specific enough that someone could build it wrong and you would notice.

| | |
| --- | --- |
| **In (proactive)** | Scheduled trigger + signal from source system (case severity, usage trend, calendar event, news item) |
| **Out (proactive)** | Alert with account name, signal summary, and 1–3 suggested actions |
| **In (reactive)** | Account name + plain-text context or question |
| **Out (reactive)** | Prioritized list of 3–5 next actions, each with category (Operations / Cadence / Renewal / Escalation) and time horizon, with source record cited |

**Source systems (v1 scope):**
- Salesforce (OrgCS/Org62) — support cases (S1/S2 priority), account health
- Anypoint Admin Portal — vCore usage trend, apps deployed/undeployed, user count
- Google Calendar — cadence calls, QBRs, EBRs, renewal discussions
- Corporate websites / public web — leadership changes, M&A, product launches

---

## Decisions made later

<!--
  Amended as the cohort goes. Keep the reasoning, not just the choice — Week 5
  asks you to defend your architecture against the options you rejected, and
  Week 10's handoff doc is largely this section.
-->

| Week | Decision | Why, and what you rejected |
| --- | --- | --- |
| 3 | Retrieval approach | <!-- TC3 --> |
| 5 | Agent architecture | <!-- TC5 --> |
| 8 | Model | <!-- TC8 --> |
