import os
os.environ["GCE_METADATA_HOST"] = "127.0.0.1:9999"

import google.auth
from google.auth.exceptions import DefaultCredentialsError
google.auth.default = lambda *a, **kw: (_ for _ in ()).throw(DefaultCredentialsError("GCP metadata blocked in favor of API Key"))

from fastapi.staticfiles import StaticFiles
import asyncio
import json
import uuid
from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .agent import root_agent
from .events import EventEmitter
from .runner import ADKRunner
from .schemas import InvestigationResult


app = FastAPI(title="ShotOps Agent Backend")

runner = ADKRunner(root_agent)

investigations: Dict[str, dict] = {}


class CreateInvestigationRequest(BaseModel):
    query: str



@app.get("/health")
def health_check():
    import os
    from .config import settings
    return {
        "status": "ok",
        "google_key_prefix": (os.getenv("GOOGLE_API_KEY") or "")[:6],
        "google_key_len": len(os.getenv("GOOGLE_API_KEY") or ""),
        "gemini_key_prefix": (os.getenv("GEMINI_API_KEY") or "")[:6],
        "grafana_url": os.getenv("GRAFANA_URL", ""),
        "grafana_key_prefix": (os.getenv("GRAFANA_API_KEY") or "")[:6],
    }

@app.post("/investigations")
async def create_investigation(req: CreateInvestigationRequest):
    investigation_id = str(uuid.uuid4())

    emitter = EventEmitter(investigation_id)

    task = asyncio.create_task(
        runner.run_investigation(
            investigation_id,
            req.query,
            emitter,
        )
    )

    investigations[investigation_id] = {
        "query": req.query,
        "status": "running",
        "emitter": emitter,
        "task": task,
    }

    return {
        "investigationId": investigation_id,
        "status": "running",
    }


@app.get("/investigations/{investigation_id}")
async def get_investigation(investigation_id: str):
    investigation = investigations.get(investigation_id)

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    task = investigation["task"]
    emitter = investigation["emitter"]

    if not task.done():
        return {
            "investigationId": investigation_id,
            "status": "running",
            "query": investigation["query"],
        }

    events = emitter.get_all_events()

    final_text = None

    for event in reversed(events):
        if event.eventType == "COMPLETED" and event.outputSummary:
            final_text = event.outputSummary
            break

    status = "completed" if final_text else "failed"

    result = InvestigationResult(
        investigationId=investigation_id,
        status=status,
        query=investigation["query"],
        rootCause=final_text,
        confidence=0.0,
        evidence=[],
        recommendation=None,
        events=events,
    )

    return result.model_dump()


@app.get("/investigations/{investigation_id}/events")
async def stream_events(
    investigation_id: str,
    request: Request,
):
    investigation = investigations.get(investigation_id)

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    emitter = investigation["emitter"]

    async def event_generator():
        # Send events that already exist.
        for event in emitter.get_all_events():
            yield f"data: {json.dumps(event.model_dump())}\n\n"

        queue = asyncio.Queue()

        def listener(event):
            queue.put_nowait(event)

        emitter.subscribe(listener)

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(
                        queue.get(),
                        timeout=15,
                    )

                    yield (
                        f"data: "
                        f"{json.dumps(event.model_dump())}"
                        f"\n\n"
                    )

                    if event.eventType in {"COMPLETED", "FAILED"}:
                        break

                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"

        finally:
            if listener in emitter.listeners:
                emitter.listeners.remove(listener)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
