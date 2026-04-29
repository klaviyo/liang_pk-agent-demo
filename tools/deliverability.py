import json

_MOCK_DELIVERABILITY = {
    "mail.example.com": {
        "domain": "mail.example.com",
        "reputation_score": 62,
        "reputation_label": "Fair",
        "spf_valid": True,
        "dkim_valid": True,
        "dmarc_policy": "none",
        "dmarc_valid": False,
        "sending_ip": "198.51.100.45",
        "ip_reputation": "Good",
        "ip_blacklisted": False,
        "bounce_rate_30d_pct": 5.8,
        "spam_complaint_rate_30d_pct": 0.19,
        "open_rate_30d_pct": 18.4,
        "issues": [
            "DMARC policy is 'none' — not enforced; upgrade to 'quarantine' or 'reject'",
            "Bounce rate (5.8%) exceeds recommended threshold of 2%",
            "Spam complaint rate (0.19%) is above 0.1% industry threshold",
        ],
    },
    "sends.acme.io": {
        "domain": "sends.acme.io",
        "reputation_score": 91,
        "reputation_label": "Excellent",
        "spf_valid": True,
        "dkim_valid": True,
        "dmarc_policy": "reject",
        "dmarc_valid": True,
        "sending_ip": "198.51.100.200",
        "ip_reputation": "Excellent",
        "ip_blacklisted": False,
        "bounce_rate_30d_pct": 0.9,
        "spam_complaint_rate_30d_pct": 0.02,
        "open_rate_30d_pct": 31.2,
        "issues": [],
    },
}


def handle(input: dict) -> str:
    domain = input.get("domain", "")
    account_id = input.get("account_id", "")

    if not domain and not account_id:
        return json.dumps({"error": "Provide either 'domain' or 'account_id'"})

    if not domain:
        domain_map = {"ACC-1001": "mail.example.com", "ACC-1002": "sends.acme.io"}
        domain = domain_map.get(account_id, "")

    data = _MOCK_DELIVERABILITY.get(domain)
    if not data:
        return json.dumps({"error": f"No deliverability data found for domain {domain!r}"})
    return json.dumps(data)
