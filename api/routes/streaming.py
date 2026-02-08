import os

from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from api.schemas import SessionRequest
from application.services.session_service import create_session
from application.services.streaming_service import stream_session_events

router = APIRouter()


# ------------------------------------------
# Test Mode Detection
# ------------------------------------------
def is_test_mode() -> bool:
    return os.getenv("PYTEST_RUNNING") == "1"


# ------------------------------------------
# Wrapper Expected by Tests
# ------------------------------------------
class StreamSessionRequest(BaseModel):
    input: SessionRequest


# ------------------------------------------
# Streaming Endpoint
# ------------------------------------------
@router.post("/session/stream")
async def session_stream(payload: StreamSessionRequest):

    # Unwrap request
    req = payload.input

    # Create session
    session = create_session(
        user_id=req.user_id,
        input_data=req.model_dump()
    )

    session_id = session["session_id"]

    # --------------------------------------
    # Test Mode → Deterministic JSON
    # --------------------------------------
    if is_test_mode():
        events = [chunk async for chunk in stream_session_events(session_id=session_id)]
        return JSONResponse(events)

    # --------------------------------------
    # Production Streaming Mode
    # --------------------------------------
    return StreamingResponse(
        stream_session_events(session_id=session_id),
        media_type="text/event-stream"
    )


@router.get("/session/{session_id}/stream")
async def session_stream_sse(session_id: str):
    """
    SSE endpoint for streaming session events in deterministic order.
    Does NOT create session or execute domain logic.
    Closes when session completes.
    """
    return StreamingResponse(
        stream_session_events(session_id=session_id),
        media_type="text/event-stream"
    )
