import json
from anthropic import Anthropic
from agent.prompts import VALIDATION_SYSTEM


def run(draft_response: str, original_question: str, tool_results_summary: str, client: Anthropic) -> str:
    """Validate a draft response and return the final (possibly improved) response text."""
    prompt = (
        f"## Customer's original question\n{original_question}\n\n"
        f"## Tool results used to answer\n{tool_results_summary}\n\n"
        f"## Draft response to validate\n{draft_response}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[{"type": "text", "text": VALIDATION_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip() if response.content else ""

    try:
        # Strip markdown code fences if present
        text = raw
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

        data = json.loads(text)
        final = data.get("response", draft_response)
        return final if final else draft_response
    except (json.JSONDecodeError, KeyError):
        # Validation agent returned unparseable output — fall back to draft
        return draft_response
