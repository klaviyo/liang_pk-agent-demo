import json
from anthropic import Anthropic
from agent.prompts import ORCHESTRATOR_SYSTEM
from agent.state import ConversationState
from tools.registry import TOOL_SCHEMAS, dispatch
from subagents import diagnostics_agent, validation_agent

_MAX_TOOL_CALLS = 10


class Orchestrator:
    def __init__(self, client: Anthropic):
        self.client = client
        self.state = ConversationState()
        self._tool_results_log: list[str] = []
        self._original_question: str = ""

    def handle_message(self, user_input: str) -> str:
        if self.state.clarification_pending:
            self.state.messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": self.state.pending_tool_use_id,
                        "content": user_input,
                    }
                ],
            })
            self.state.clarification_pending = False
            self.state.pending_tool_use_id = None
        else:
            self._original_question = user_input
            self._tool_results_log = []
            self.state.tool_call_count = 0
            self.state.messages.append({"role": "user", "content": user_input})

        return self._run_loop()

    def _run_loop(self) -> str:
        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=[{"type": "text", "text": ORCHESTRATOR_SYSTEM, "cache_control": {"type": "ephemeral"}}],
                tools=TOOL_SCHEMAS,
                messages=self.state.messages,
                cache_control={"type": "ephemeral"},
            )

            self.state.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                text_blocks = [b.text for b in response.content if hasattr(b, "text")]
                draft = text_blocks[0] if text_blocks else "I'm sorry, I couldn't generate a response."
                return self._validate(draft)

            if response.stop_reason == "tool_use":
                tool_results = []
                clarification_triggered = False

                for block in response.content:
                    if not hasattr(block, "type") or block.type != "tool_use":
                        continue

                    self.state.tool_call_count += 1

                    if self.state.tool_call_count > _MAX_TOOL_CALLS:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps({"error": "Tool call limit reached."}),
                            "is_error": True,
                        })
                        continue

                    if block.name == "ask_clarification":
                        question = block.input.get("question", "Could you please clarify your question?")
                        self.state.clarification_pending = True
                        self.state.pending_tool_use_id = block.id
                        clarification_triggered = True
                        return question

                    elif block.name == "run_diagnostics_agent":
                        result = diagnostics_agent.run(
                            account_id=block.input.get("account_id", ""),
                            problem_description=block.input.get("problem_description", ""),
                            client=self.client,
                        )
                        self._tool_results_log.append(f"[diagnostics_agent]: {result}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                    else:
                        result = dispatch(block.name, block.input)
                        self._tool_results_log.append(f"[{block.name}]: {result}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                if not clarification_triggered:
                    self.state.messages.append({"role": "user", "content": tool_results})

                if self.state.tool_call_count > _MAX_TOOL_CALLS:
                    draft = "I've reached the maximum number of tool calls for this request. Based on what I've gathered so far, I may not have complete information. Please try rephrasing your question or contact support directly."
                    return self._validate(draft)

    def _validate(self, draft: str) -> str:
        tool_summary = "\n".join(self._tool_results_log) if self._tool_results_log else "No tools were called."
        return validation_agent.run(
            draft_response=draft,
            original_question=self._original_question,
            tool_results_summary=tool_summary,
            client=self.client,
        )
