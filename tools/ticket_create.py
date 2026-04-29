import json
import uuid
from datetime import datetime, timezone


def handle(input: dict) -> str:
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    ticket = {
        "ticket_id": ticket_id,
        "status": "open",
        "priority": input.get("priority", "medium"),
        "subject": input.get("subject", "Customer Support Request"),
        "description": input.get("description", ""),
        "account_id": input.get("account_id", "unknown"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "estimated_response_time": "2-4 business hours",
        "message": (
            f"Ticket {ticket_id} created and assigned to the support team. "
            "You'll receive a confirmation email shortly."
        ),
    }
    return json.dumps(ticket)
