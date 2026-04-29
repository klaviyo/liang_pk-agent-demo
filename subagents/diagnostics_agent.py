import json
from anthropic import Anthropic
from agent.prompts import DIAGNOSTICS_SYSTEM
from tools.registry import TOOL_SCHEMAS, dispatch

_DIAGNOSTICS_TOOLS = [
    t for t in TOOL_SCHEMAS
    if t["name"] in {"account_lookup", "campaign_status", "check_deliverability", "knowledge_base_search"}
]

_MAX_TOOL_CALLS = 10
_REQUIRED_SECTIONS = ("**Root cause:**", "**Evidence:**", "**Recommended fix:**")


def validate_result(text: str) -> bool:
    return all(section in text for section in _REQUIRED_SECTIONS)


def run(account_id: str, problem_description: str, client: Anthropic) -> str:
    messages = [
        {
            "role": "user",
            "content": (
                f"Account: {account_id}\n"
                f"Problem: {problem_description}\n\n"
                "Please investigate and provide your diagnosis in the required format."
            ),
        }
    ]

    tool_calls = 0

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=[{"type": "text", "text": DIAGNOSTICS_SYSTEM, "cache_control": {"type": "ephemeral"}}],
            tools=_DIAGNOSTICS_TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            text_blocks = [b.text for b in response.content if hasattr(b, "text")]
            result = text_blocks[0] if text_blocks else ""
            if not validate_result(result):
                return (
                    "**Root cause:** Unable to determine root cause from available data.\n\n"
                    "**Evidence:**\n- Diagnostic agent did not return a complete analysis.\n\n"
                    "**Recommended fix:**\n1. Please contact Klaviyo support for a manual review.\n"
                    f"2. Raw findings: {result}"
                )
            return result

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if not hasattr(block, "type") or block.type != "tool_use":
                    continue
                tool_calls += 1
                if tool_calls > _MAX_TOOL_CALLS:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps({"error": "Tool call limit reached — stopping investigation."}),
                        "is_error": True,
                    })
                else:
                    result = dispatch(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})

            if tool_calls > _MAX_TOOL_CALLS:
                break

    return (
        "**Root cause:** Investigation exceeded tool call limit.\n\n"
        "**Evidence:**\n- Too many tool calls were required to complete the analysis.\n\n"
        "**Recommended fix:**\n1. Contact Klaviyo support for a manual investigation."
    )
