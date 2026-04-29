import json

_MOCK_ACCOUNTS = {
    "alice@example.com": {
        "account_id": "ACC-1001",
        "company": "Example Corp",
        "email": "alice@example.com",
        "plan": "Growth",
        "status": "active",
        "created_at": "2023-03-15",
        "sending_domain": "mail.example.com",
    },
    "bob@acme.io": {
        "account_id": "ACC-1002",
        "company": "Acme Industries",
        "email": "bob@acme.io",
        "plan": "Enterprise",
        "status": "active",
        "created_at": "2022-07-01",
        "sending_domain": "sends.acme.io",
    },
    "ACC-1001": {
        "account_id": "ACC-1001",
        "company": "Example Corp",
        "email": "alice@example.com",
        "plan": "Growth",
        "status": "active",
        "created_at": "2023-03-15",
        "sending_domain": "mail.example.com",
    },
    "ACC-1002": {
        "account_id": "ACC-1002",
        "company": "Acme Industries",
        "email": "bob@acme.io",
        "plan": "Enterprise",
        "status": "active",
        "created_at": "2022-07-01",
        "sending_domain": "sends.acme.io",
    },
}


def handle(input: dict) -> str:
    identifier = input.get("email") or input.get("account_id", "")
    account = _MOCK_ACCOUNTS.get(identifier)
    if not account:
        return json.dumps({"error": f"No account found for identifier: {identifier!r}"})
    return json.dumps(account)
