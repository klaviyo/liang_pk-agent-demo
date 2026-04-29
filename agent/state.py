from dataclasses import dataclass, field


@dataclass
class ConversationState:
    messages: list = field(default_factory=list)
    clarification_pending: bool = False
    pending_tool_use_id: str | None = None
    tool_call_count: int = 0
