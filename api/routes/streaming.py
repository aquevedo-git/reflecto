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

    # Deterministic async SSE streaming: do not materialize event list
    async def event_generator():
        # Inline comment: This async generator yields events in strict order as produced by stream_session_events,
        # preserving deterministic delivery and contract guarantees for SSE clients.
        async for sse_event in stream_session_events(session_id=session_id):
            # sse_event is already formatted as SSE string by the backend service
            yield sse_event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
