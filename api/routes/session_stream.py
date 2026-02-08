from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from sse_starlette.sse import EventSourceResponse
from services.streaming_service import stream_session_events

router = APIRouter()


@router.get("/session/{session_id}/stream")
async def session_stream_sse(session_id: str):
    """
    SSE endpoint for streaming session events in deterministic order.
    Does NOT create session or execute domain logic.
    Closes when session completes.
    """
    from services.streaming_service import stream_session_events
    async def event_generator():
        async for event in stream_session_events(session_id):
            yield event
    return EventSourceResponse(event_generator())
