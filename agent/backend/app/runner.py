from datetime import datetime, timezone

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .events import EventEmitter, adapt_adk_event
from .schemas import AgentEvent


class ADKRunner:
    def __init__(self, root_agent: Agent):
        self.root_agent = root_agent
        self.session_service = InMemorySessionService()

        self.runner = Runner(
            app_name="shotops",
            agent=root_agent,
            session_service=self.session_service,
        )

    async def run_investigation(
        self,
        investigation_id: str,
        query: str,
        emitter: EventEmitter,
    ):
        run_id = emitter.run_id

        session = await self.session_service.create_session(
            app_name="shotops",
            user_id="user",
            session_id=investigation_id,
        )

        emitter.emit(
            AgentEvent(
                runId=run_id,
                investigationId=investigation_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                eventType="MISSION_RECEIVED",
                status="success",
                inputSummary=query,
            )
        )

        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)],
        )

        try:
            async for adk_event in self.runner.run_async(
                user_id="user",
                session_id=session.id,
                new_message=user_content,
            ):
                shotops_event = adapt_adk_event(
                    adk_event,
                    investigation_id,
                    run_id,
                )

                if shotops_event:
                    emitter.emit(shotops_event)

        except Exception as exc:
            emitter.emit(
                AgentEvent(
                    runId=run_id,
                    investigationId=investigation_id,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    eventType="FAILED",
                    status="error",
                    outputSummary=str(exc),
                )
            )
