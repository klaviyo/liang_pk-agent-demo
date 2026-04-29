import json

_MOCK_CAMPAIGNS = {
    "ACC-1001": [
        {
            "campaign_id": "CMP-5001",
            "name": "Holiday Promo",
            "status": "sent",
            "sent_at": "2025-12-20T10:00:00Z",
            "recipients": 12450,
            "delivered": 11732,
            "bounced": 718,
            "bounce_rate_pct": 5.76,
            "opens": 3284,
            "open_rate_pct": 27.99,
            "clicks": 891,
            "click_rate_pct": 7.16,
            "spam_complaints": 24,
            "unsubscribes": 102,
            "errors": [
                {"code": "550", "message": "Mailbox does not exist", "count": 543},
                {"code": "421", "message": "Too many connections", "count": 175},
            ],
        },
        {
            "campaign_id": "CMP-5002",
            "name": "Spring Newsletter",
            "status": "scheduled",
            "scheduled_for": "2026-05-01T14:00:00Z",
            "recipients": 13100,
            "delivered": None,
            "errors": [],
        },
    ],
    "ACC-1002": [
        {
            "campaign_id": "CMP-6001",
            "name": "Q1 Re-engagement",
            "status": "sent",
            "sent_at": "2026-01-15T09:00:00Z",
            "recipients": 45000,
            "delivered": 44325,
            "bounced": 675,
            "bounce_rate_pct": 1.5,
            "opens": 8865,
            "open_rate_pct": 20.0,
            "clicks": 2215,
            "click_rate_pct": 5.0,
            "spam_complaints": 12,
            "unsubscribes": 330,
            "errors": [],
        },
    ],
}


def handle(input: dict) -> str:
    account_id = input.get("account_id", "")
    campaign_id = input.get("campaign_id")

    campaigns = _MOCK_CAMPAIGNS.get(account_id)
    if not campaigns:
        return json.dumps({"error": f"No campaigns found for account {account_id!r}"})

    if campaign_id:
        match = next((c for c in campaigns if c["campaign_id"] == campaign_id), None)
        if not match:
            return json.dumps({"error": f"Campaign {campaign_id!r} not found for account {account_id!r}"})
        return json.dumps(match)

    return json.dumps({"campaigns": campaigns})
