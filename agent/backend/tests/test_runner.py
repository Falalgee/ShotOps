import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agent import root_agent
from app.runner import ADKRunner
from app.events import EventEmitter


@pytest.mark.asyncio
async def test_runner_initialization():
    runner = ADKRunner(root_agent)

    assert runner.runner is not None
    assert runner.session_service is not None


@pytest.mark.asyncio
async def test_run_investigation_emits_events():
    runner = ADKRunner(root_agent)

    mock_event = MagicMock()
    mock_event.author = "model"
    mock_event.content = MagicMock()
    mock_event.content.parts = [MagicMock(text="Test response")]
    mock_event.is_final_response.return_value = True

    async def fake_run_async(**kwargs):
        yield mock_event

    runner.runner.run_async = fake_run_async

    emitter = EventEmitter("test-inv")

    await runner.run_investigation(
        "test-inv",
        "Why?",
        emitter,
    )

    events = emitter.get_all_events()

    assert len(events) >= 2
