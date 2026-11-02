SALESFORCE_CASES_AXES = {
    "case_severity": [
        "S1 — Production down, all integrations failing, immediate action required",
        "S2 — Critical degradation, transactions partially failing, urgent response",
        "S3 or S4 — Non-critical issue or general inquiry, standard response",
    ],
    "case_type": [
        "Integration Failure — transactions not processing end-to-end",
        "Connectivity — end systems cannot reach Anypoint services",
        "Platform Access — unable to log into Anypoint Portal",
    ],
    "decline": [
        "Request to share another customer's case details — privacy violation",
        "Request to modify or close cases outside CSM authority",
    ],
}

MULESOFT_ADMIN_AXES = {
    "vcore_trend": [
        "Increasing — approaching capacity limit, expansion conversation needed",
        "Stable — consistent healthy usage, no action required",
        "Declining — negative adoption signal, potential attrition risk",
    ],
    "app_event": [
        "New application deployed — positive expansion signal",
        "Application undeployed — potential churn signal, investigation needed",
        "User count declining — engagement risk, intervention needed",
    ],
    "decline": [
        "Request to modify Anypoint platform configuration — outside CSM scope",
        "Request for customer admin credentials or production access",
    ],
}

CALENDAR_AXES = {
    "meeting_type": [
        "Cadence Call — routine account health check-in",
        "QBR or EBR — business review with metrics and roadmap",
        "Renewal Discussion — contract, pricing, and expansion scope",
    ],
    "prep_urgency": [
        "This week — immediate preparation needed",
        "Next month — strategic preparation, long lead time",
    ],
    "decline": [
        "Request to view another CSM's account meetings",
        "Request to schedule a personal or non-account meeting",
    ],
}

SIGNATURE_SUCCESS_AXES = {
    "enrollment_tenure": [
        "Enrolled < 3 months ago — baseline period, adoption still ramping",
        "Enrolled 6–12 months ago — mid-term, enough data to show trend",
        "Enrolled 12+ months ago — mature, full before/after comparison available",
    ],
    "adoption_trend": [
        "vCore and app count increasing since enrollment — adoption growing",
        "vCore and app count stable since enrollment — flat adoption, value unclear",
        "vCore or app count declining since enrollment — adoption not improving, renewal risk",
    ],
    "decline": [
        "Request to access another account's Signature Success data",
        "Request to modify Signature Success entitlements — outside CSM authority",
    ],
}

CORPORATE_NEWS_AXES = {
    "news_type": [
        "M&A or Funding — ownership or organizational change",
        "Leadership Change — new CTO, CDO, VP Engineering, or IT head",
        "Product Launch or Market Expansion — new business line or region",
    ],
    "csm_implication": [
        "Expansion opportunity — new integration or automation use case",
        "Account risk — potential budget cut, reprioritization, or churn signal",
    ],
    "decline": [
        "Request for confidential or non-public company information",
        "News inquiry about a company not in the CSM's managed accounts",
    ],
}
