from tools import account_lookup, billing_lookup, campaign_status, deliverability, knowledge_base, ticket_create

TOOL_SCHEMAS = [
    {
        "name": "account_lookup",
        "description": "Look up a Klaviyo account by email address or account ID. Returns account details including plan, status, and sending domain. Always call this first before using campaign, billing, or deliverability tools.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Customer's email address",
                },
                "account_id": {
                    "type": "string",
                    "description": "Klaviyo account ID (e.g. ACC-1001)",
                },
            },
        },
    },
    {
        "name": "ask_clarification",
        "description": "Ask the customer a clarifying question when their request is ambiguous or missing required information (e.g., which account, which campaign). Use this instead of guessing. The customer's reply will be returned as your tool result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The specific question to ask the customer",
                },
            },
            "required": ["question"],
        },
    },
    {
        "name": "campaign_status",
        "description": "Get delivery statistics and error details for one or all campaigns on an account. Returns sent/bounced/open/click counts and error codes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Klaviyo account ID (required)",
                },
                "campaign_id": {
                    "type": "string",
                    "description": "Specific campaign ID to fetch. Omit to list all campaigns for the account.",
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "check_deliverability",
        "description": "Check email deliverability metrics for an account's sending domain: reputation score, SPF/DKIM/DMARC status, bounce rate, spam complaint rate, and any flagged issues.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Klaviyo account ID — used to resolve the sending domain",
                },
                "domain": {
                    "type": "string",
                    "description": "Sending domain to check directly (alternative to account_id)",
                },
            },
        },
    },
    {
        "name": "create_ticket",
        "description": "Escalate an issue to a human support agent by creating a support ticket. Use only when the issue cannot be resolved with available tools.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Klaviyo account ID",
                },
                "subject": {
                    "type": "string",
                    "description": "Short summary of the issue",
                },
                "description": {
                    "type": "string",
                    "description": "Full description of the issue including what has been tried",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                    "description": "Ticket priority",
                },
            },
            "required": ["account_id", "subject", "description"],
        },
    },
    {
        "name": "get_billing_info",
        "description": "Get billing information for an account: current plan, pricing, payment status, contact and email usage for the current billing cycle, and any overage charges.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Klaviyo account ID (required)",
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "knowledge_base_search",
        "description": "Search Klaviyo's knowledge base for help articles. Use for general how-to questions, feature questions, or to find documentation about Klaviyo functionality.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query — keywords or a question",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "run_diagnostics_agent",
        "description": "Delegate a complex, multi-step diagnostic investigation to a specialist sub-agent. Use for problems like declining open rates, deliverability issues, or campaign failures that require analysis across multiple data sources. Returns a structured Root cause / Evidence / Recommended fix report.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Klaviyo account ID to investigate",
                },
                "problem_description": {
                    "type": "string",
                    "description": "Detailed description of the problem to investigate",
                },
            },
            "required": ["account_id", "problem_description"],
        },
    },
]

_HANDLERS = {
    "account_lookup": account_lookup.handle,
    "campaign_status": campaign_status.handle,
    "check_deliverability": deliverability.handle,
    "create_ticket": ticket_create.handle,
    "get_billing_info": billing_lookup.handle,
    "knowledge_base_search": knowledge_base.handle,
}


def dispatch(name: str, input: dict) -> str:
    handler = _HANDLERS.get(name)
    if not handler:
        return f'{{"error": "Unknown tool: {name}"}}'
    return handler(input)
