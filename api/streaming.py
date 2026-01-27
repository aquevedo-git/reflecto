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

router = APIRouter()


async def stream_generator(session_id: str, request: Request, shutdown_event: asyncio.Event):
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
            hour = now.hour

            if 5 <= hour < 12:
                time_of_day = "morning"
                state = "AWAKE"
            elif 12 <= hour < 17:
                time_of_day = "afternoon"
                state = "AWAKE"
            elif 17 <= hour < 22:
                time_of_day = "evening"
                state = "CALM"
            else:
                time_of_day = "night"
                state = "SLEEPING"

            now_ts = time.time() - start
            emitted = False

            # Heartbeat
            if now_ts - last_heartbeat >= heartbeat_interval:
                print("[SSE] heartbeat")
                yield f"event: heartbeat\ndata: {json.dumps({'ts': int(time.time())})}\n\n"
                last_heartbeat = now_ts
                emitted = True

            # Presence
            if now_ts - last_presence >= presence_interval:
                print(f"[SSE] presence={state}")
                yield f"event: presence\ndata: {json.dumps({'state': state, 'time_of_day': time_of_day})}\n\n"
                last_presence = now_ts
                emitted = True

            # Skills
            if now_ts - last_skills >= skills_interval:
                print("[SSE] skills update")
                yield f"event: skills\ndata: {json.dumps({'financial':80,'health':70,'focus':90,'relationships':60})}\n\n"
                last_skills = now_ts
                emitted = True

            # Time of day
            if now_ts - last_time_of_day >= time_of_day_interval:
                print(f"[SSE] time_of_day={time_of_day}")
                yield f"event: time_of_day\ndata: {json.dumps({'time_of_day': time_of_day})}\n\n"
                last_time_of_day = now_ts
                emitted = True

            if not emitted:
                await asyncio.sleep(0.1)  # cancellable

    except asyncio.CancelledError:
        print("[SSE] cancelled by server")
        raise  # IMPORTANT: allow uvicorn to stop immediately

    finally:
        print("[SSE] cleanup complete")


@router.get("/stream/{session_id}")
async def session_stream(session_id: str, request: Request):
    from api.main import shutdown_event

    return StreamingResponse(
        stream_generator(session_id, request, shutdown_event),
        media_type="text/event-stream"
    )
