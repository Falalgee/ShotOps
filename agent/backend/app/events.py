import uuid
from datetime import datetime, timezone
from typing import Callable, List, Optional

from .schemas import AgentEvent


class EventEmitter:
    def __init__(self, investigation_id: str):
        self.investigation_id = investigation_id
        self.run_id = str(uuid.uuid4())
        self.listeners: List[Callable[[AgentEvent], None]] = []
        self.events: List[AgentEvent] = []

    def subscribe(self, callback: Callable[[AgentEvent], None]):
        self.listeners.append(callback)

    def emit(self, event: AgentEvent):
        self.events.append(event)

        for callback in self.listeners:
            callback(event)

    def get_all_events(self) -> List[AgentEvent]:
        return self.events


def adapt_adk_event(
    adk_event,
    investigation_id: str,
    run_id: str,
) -> Optional[AgentEvent]:
    """Convert a Google ADK event into a ShotOps AgentEvent."""

    author = getattr(adk_event, "author", None)
    content = getattr(adk_event, "content", None)
    invocation_id = getattr(adk_event, "invocation_id", None)
    adk_timestamp = getattr(adk_event, "timestamp", None)

    is_final = getattr(adk_event, "is_final_response", None)

    if callable(is_final):
        is_final = is_final()

    # Extract text from ADK Content parts.
    text_parts = []

    if content and hasattr(content, "parts"):
        for part in content.parts:
            text = getattr(part, "text", None)

            if text:
                text_parts.append(text)

    output_text = "\n".join(text_parts) if text_parts else None

    # Map ADK events to the ShotOps event schema.
    if author == "user":
        event_type = "MISSION_RECEIVED"
        status = "success"

    elif is_final:
        event_type = "COMPLETED"
        status = "success"

    elif author == "model":
        event_type = "INTENT_ANALYSIS"
        status = "success"

    elif author and "tool" in author.lower():
        event_type = "TOOL_CALL_STARTED"
        status = "running"

    else:
        event_type = "ADK_EVENT"
        status = "success"

    metadata = {
        "adk_author": author,
        "adk_invocation_id": invocation_id,
        "adk_timestamp": (
            adk_timestamp.isoformat()
            if adk_timestamp and hasattr(adk_timestamp, "isoformat")
            else adk_timestamp
        ),
    }

    return AgentEvent(
        runId=run_id,
        investigationId=investigation_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        eventType=event_type,
        status=status,
        agent=author,
        outputSummary=output_text,
        metadata=metadata,
    )
