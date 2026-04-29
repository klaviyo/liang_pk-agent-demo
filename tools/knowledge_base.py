import json

_KB_ARTICLES = [
    {
        "id": "KB-001",
        "title": "Klaviyo daily sending limits",
        "content": (
            "Klaviyo sending limits depend on your plan. Free plan: 500 emails/day. "
            "Email plan: scales with your contact count (roughly 5× your contact limit per day). "
            "Growth and Pro plans: no hard daily cap — throttled automatically to protect deliverability. "
            "Enterprise plans have custom limits negotiated with your account manager."
        ),
        "tags": ["sending", "limits", "daily", "plan"],
    },
    {
        "id": "KB-002",
        "title": "How to warm up a new sending domain",
        "content": (
            "Domain warming is critical for new senders. Start with your most engaged subscribers. "
            "Week 1: send to 500–1000 recipients. Week 2: double the volume. Continue doubling weekly "
            "until you reach your target volume. Monitor bounce rates (keep under 2%) and spam complaint "
            "rates (keep under 0.1%). Use Klaviyo's deliverability dashboard to track reputation."
        ),
        "tags": ["domain", "warming", "deliverability", "new"],
    },
    {
        "id": "KB-003",
        "title": "Understanding bounce types in Klaviyo",
        "content": (
            "Hard bounces: permanent failures (invalid address, domain doesn't exist). Klaviyo "
            "automatically suppresses hard-bounced addresses. Soft bounces: temporary failures "
            "(mailbox full, server temporarily unavailable). After 3 consecutive soft bounces, "
            "Klaviyo suppresses the address. Check the Suppressions tab under Lists & Segments."
        ),
        "tags": ["bounce", "hard bounce", "soft bounce", "suppression"],
    },
    {
        "id": "KB-004",
        "title": "Why are my open rates low?",
        "content": (
            "Common causes of low open rates: (1) Subject line isn't compelling — try A/B testing. "
            "(2) Sending to unengaged contacts — segment to engaged-only lists. "
            "(3) Poor send time — use Klaviyo's Smart Send Time feature. "
            "(4) Spam folder delivery — check your domain reputation and authentication (SPF, DKIM, DMARC). "
            "(5) List fatigue — reduce send frequency or sunset inactive subscribers."
        ),
        "tags": ["open rate", "deliverability", "subject line", "engagement"],
    },
    {
        "id": "KB-005",
        "title": "Setting up SPF, DKIM, and DMARC for Klaviyo",
        "content": (
            "SPF: Add 'include:spf.klaviyo.com' to your DNS TXT record. "
            "DKIM: Klaviyo generates keys automatically — verify in Account > Settings > Sending Domains. "
            "DMARC: Add a TXT record '_dmarc.yourdomain.com' with policy 'p=quarantine' or 'p=reject' "
            "once SPF and DKIM are verified. Use a monitoring-only policy (p=none) first to avoid "
            "losing legitimate mail. Check dmarc.org for record format examples."
        ),
        "tags": ["SPF", "DKIM", "DMARC", "authentication", "DNS"],
    },
    {
        "id": "KB-006",
        "title": "How to upgrade or downgrade your Klaviyo plan",
        "content": (
            "To change your plan: go to Account > Billing > Plan & Pricing. "
            "Upgrades take effect immediately and are prorated. "
            "Downgrades take effect at the start of your next billing cycle. "
            "If you need a custom Enterprise plan, contact your account manager or email sales@klaviyo.com."
        ),
        "tags": ["billing", "plan", "upgrade", "downgrade", "pricing"],
    },
]


def handle(input: dict) -> str:
    query = input.get("query", "").lower()
    if not query:
        return json.dumps({"error": "query is required"})

    query_terms = set(query.split())
    results = []
    for article in _KB_ARTICLES:
        searchable = (article["title"] + " " + article["content"] + " " + " ".join(article["tags"])).lower()
        score = sum(1 for term in query_terms if term in searchable)
        if score > 0:
            results.append({"score": score, "article": article})

    results.sort(key=lambda x: x["score"], reverse=True)
    top = [r["article"] for r in results[:3]]

    if not top:
        return json.dumps({"results": [], "message": "No relevant articles found."})
    return json.dumps({"results": top})
