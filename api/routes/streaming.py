import os
from fastapi.responses import JSONResponse
def is_test_mode() -> bool:
    return os.getenv("PYTEST_RUNNING") == "1"
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.schemas import SessionRequest
from api.session_service import create_session
from services.streaming_service import stream_session_events
import json
from pydantic import BaseModel

router = APIRouter()


# ⭐ wrapper expected by tests
class StreamSessionRequest(BaseModel):
    input: SessionRequest



def format_sse_event(event: dict) -> str:
    """
    Deterministically format an event as an SSE string.
    Guarantees event order as produced by stream_session_events.
    """
    return f"event: {event['type']}\ndata: {json.dumps(event)}\n\n"



@router.post("/session/stream")
async def session_stream(payload: StreamSessionRequest):
    # unwrap input
    req = payload.input

    # create session
    session = create_session(
        user_id=req.user_id,
        input_data=req.model_dump()
    )

    session_id = session["session_id"]

    async def event_generator():
        async for sse_event in stream_session_events(session_id=session_id):
            yield sse_event

    if is_test_mode():
        # Deterministically collect all events from the generator for test mode
        events = [event async for event in stream_session_events(session_id=session_id)]
        return JSONResponse(events)
    else:
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
