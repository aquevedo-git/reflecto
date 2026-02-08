import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from application.services.streaming_service import stream_session_events

router = APIRouter()



@router.get("/session/{session_id}/stream")
async def session_stream_sse(session_id: str):
    """
    SSE endpoint for streaming session events in deterministic order.
    Does NOT create session or execute domain logic.
    Closes when session completes.
    """
    logging.debug("STREAM ROUTE RETURNING StreamingResponse")
    # Directly return the async generator in StreamingResponse
    return StreamingResponse(
        stream_session_events(session_id),
        media_type="text/event-stream"
    )
