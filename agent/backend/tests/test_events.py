from unittest.mock import MagicMock

from app.events import adapt_adk_event


def test_adapt_adk_event_final():
    class FakeEvent:
        author = "model"
        content = MagicMock()
        content.parts = [MagicMock(text="Final answer")]
        is_final_response = lambda self: True
        invocation_id = "123"
        timestamp = None

    event = FakeEvent()

    result = adapt_adk_event(
        event,
        "inv1",
        "run1",
    )

    assert result.eventType == "COMPLETED"
    assert result.outputSummary == "Final answer"
