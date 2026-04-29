import json

_MOCK_BILLING = {
    "ACC-1001": {
        "account_id": "ACC-1001",
        "plan": "Growth",
        "monthly_price_usd": 150,
        "billing_cycle_start": "2026-04-01",
        "billing_cycle_end": "2026-04-30",
        "payment_status": "current",
        "payment_method": "Visa ending in 4242",
        "contacts_included": 15000,
        "contacts_used": 12450,
        "emails_sent_this_cycle": 37350,
        "emails_included": 150000,
        "overage_rate_per_1k": 1.50,
        "overage_charges_usd": 0,
        "next_invoice_date": "2026-05-01",
        "next_invoice_estimate_usd": 150,
    },
    "ACC-1002": {
        "account_id": "ACC-1002",
        "plan": "Enterprise",
        "monthly_price_usd": 2400,
        "billing_cycle_start": "2026-04-01",
        "billing_cycle_end": "2026-04-30",
        "payment_status": "current",
        "payment_method": "ACH bank transfer",
        "contacts_included": 500000,
        "contacts_used": 412000,
        "emails_sent_this_cycle": 1250000,
        "emails_included": 5000000,
        "overage_rate_per_1k": 0.80,
        "overage_charges_usd": 0,
        "next_invoice_date": "2026-05-01",
        "next_invoice_estimate_usd": 2400,
    },
}


def handle(input: dict) -> str:
    account_id = input.get("account_id", "")
    data = _MOCK_BILLING.get(account_id)
    if not data:
        return json.dumps({"error": f"No billing data found for account {account_id!r}"})
    return json.dumps(data)
