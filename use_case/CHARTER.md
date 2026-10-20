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

A chat interface that gives a CSM the next best action along with the tools and data to complete it.

**Input → Output.** Be specific enough that someone could build it wrong and you
would notice.

| | |
| --- | --- |
| **In** | Account name + plain-text context (meeting notes, open items, renewal date, health signals) |
| **Out** | Prioritized list of 3–5 next actions, each with category (Operations / Cadence / Renewal) and time horizon|

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
