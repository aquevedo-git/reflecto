from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from api.schemas import SessionRequest
from api.session_service import create_session
from services.streaming_service import stream_session_events
from pydantic import BaseModel

router = APIRouter()


# ⭐ wrapper expected by tests
class StreamSessionRequest(BaseModel):
    input: SessionRequest


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

    # stream events deterministically
    events = list(stream_session_events(session_id=session_id))

    return PlainTextResponse("".join(events))
