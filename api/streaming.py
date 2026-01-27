"""
API endpoint for streaming session responses using Server-Sent Events (SSE).
HARD-CANCEL SAFE — production version
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import time
import json
import datetime

from api.services.action_store import get_actions
from api.services.presence_engine import derive_presence
from api.contracts import validate_event

from persistence.session_repository import SessionRepository
from uuid import uuid4

repo = SessionRepository()

router = APIRouter()

def journal_event(session_id: str, event_type: str, payload: dict, source: str = "system"):
    event = {
        "id": str(uuid4()),
        "session_id": session_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "type": event_type,
        "payload": payload,
        "source": source
    }
    repo.append_event(event)


async def stream_generator(
    session_id: str,
    request: Request,
    shutdown_event: asyncio.Event
):
    presence_interval = 3
    skills_interval = 5
    time_of_day_interval = 10
    heartbeat_interval = 3

    last_presence = 0
    last_skills = 0
    last_time_of_day = 0
    last_heartbeat = 0
    start = time.time()

    try:
        while not shutdown_event.is_set():

            # HARD EXIT: client disconnect
            if await request.is_disconnected():
                print("[SSE] client disconnected")
                return

            now = datetime.datetime.now()
            now_ts = time.time() - start
            emitted = False

            # =========================
            # HEARTBEAT
            # =========================
            if now_ts - last_heartbeat >= heartbeat_interval:
                data = {"ts": int(time.time())}
                validate_event("heartbeat", data)

                print("[SSE] heartbeat")
                journal_event(session_id, "heartbeat", data)
                yield f"event: heartbeat\ndata: {json.dumps(data)}\n\n"


                last_heartbeat = now_ts
                emitted = True

            # =========================
            # PRESENCE (DERIVED FROM ACTIONS)
            # =========================
            if now_ts - last_presence >= presence_interval:
                actions = get_actions(session_id)
                presence = derive_presence(actions, now)
                data = presence.model_dump(mode="json")

                validate_event("presence", data)

                print(f"[SSE] presence={presence.state}")
                journal_event(session_id, "presence", data)
                yield f"event: presence\ndata: {json.dumps(data)}\n\n"


                last_presence = now_ts
                emitted = True

            # =========================
            # SKILLS (TEMP STATIC)
            # =========================
            if now_ts - last_skills >= skills_interval:
                data = {
                    "financial": 80,
                    "health": 70,
                    "focus": 90,
                    "relationships": 60
                }
                validate_event("skills", data)

                print("[SSE] skills update")
                journal_event(session_id, "skills", data)
                yield f"event: skills\ndata: {json.dumps(data)}\n\n"


                last_skills = now_ts
                emitted = True

            # =========================
            # TIME OF DAY (FROM PRESENCE)
            # =========================
            if now_ts - last_time_of_day >= time_of_day_interval:
                # presence is always available because presence interval < time_of_day interval
                data = {"time_of_day": presence.time_of_day}
                validate_event("time_of_day", data)

                print(f"[SSE] time_of_day={presence.time_of_day}")
                journal_event(session_id, "time_of_day", data)
                yield f"event: time_of_day\ndata: {json.dumps(data)}\n\n"


                last_time_of_day = now_ts
                emitted = True

            if not emitted:
                await asyncio.sleep(0.1)

    except asyncio.CancelledError:
        print("[SSE] cancelled by server")
        raise

    finally:
        print("[SSE] cleanup complete")


@router.get("/stream/{session_id}")
async def session_stream(session_id: str, request: Request):
    from api.main import shutdown_event

    return StreamingResponse(
        stream_generator(session_id, request, shutdown_event),
        media_type="text/event-stream"
    )
