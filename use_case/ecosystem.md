# The ecosystem you deploy into

Where your application would actually run, inside your actual firm.

> **Week 1 starts this file. Week 9 finishes it.**
> TC1 Step 10 asks eight questions. The full Week 9 checklist has around thirty,
> and the eight are a strict subset — so nothing here gets thrown away.

Describe patterns, not specifics. "On-prem OpenShift, images from an internal
registry, no public egress" is useful to everyone and identifies nobody. Never
put real hostnames, IPs, or architecture diagrams in this file.

---

## Week 1 — the first eight questions

<!-- Answered in TC1 Step 10. Bring these back from a real conversation. -->

**Who did you ask?** (role, not name)

Director, Customer Success

| # | Question | Answer |
| :---: | --- | --- |
| 1 | Where do internal apps run? (k8s, ECS, App Service, a VM someone maintains) | EKS (AWS Elastic Kubernetes Service) — or distributed as a Docker image for local runs |
| 2 | Which cloud? AWS, Azure, GCP, on-prem, several? | AWS (primary); Azure OpenAI used for the LLM endpoint |
| 3 | Is there an internal container registry? | To be confirmed with platform team |
| 4 | How do users log in? (Okta, Entra ID, Ping, SAML, homegrown) | Okta SSO |
| 5 | Can the app reach the internet? Egress proxy? Allowlist? | Yes — Azure OpenAI is whitelisted for all corporate systems |
| 6 | Where do secrets come from? (Vault, Secrets Manager, Key Vault) | To be confirmed with platform team |
| 7 | Who approves a deployment, and what review does it need? | <!-- --> |
| 8 | Is there an approved internal LLM endpoint already? | <!-- --> |

**What surprised you?**

<!-- your answer here -->

**What would you have to change about your app to deploy there?**

<!-- your answer here -->

---

## Week 1 — what your machine told you

Oct 8, 2026

host	why	status	signed by
pypi.org	Python packages	OK	GlobalSign nv-sa
files.pythonhosted.org	the actual wheel downloads	OK	GlobalSign nv-sa
api.openai.com	the model API	OK	Google Trust Services
cdn.jsdelivr.net	the CDN the Week 1 frontend uses	OK	Sectigo Limited
huggingface.co	open weights, Weeks 2 and 8	OK	Amazon
registry-1.docker.io	container images	OK	Amazon
github.com	this repository	OK	Sectigo Limited
Verdict: Open network, public CAs, no proxy. Nothing here will bite you.

**Does this match what you were told in the table above?** Where it doesn't, that
gap is worth chasing — it usually means a proxy nobody documented.

---

## Week 9 — the full checklist

<!--
  TC9 extends this same file. Do not start a new one: the point is that the git
  history shows one continuous piece of work from Week 1 to Week 9.
-->

<!-- Week 9 -->
