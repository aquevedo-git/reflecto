from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from api.schemas import SessionRequest
from application.services.session_service import create_session

router = APIRouter()

class StartSessionResponse(BaseModel):
    session_id: str
    status: str


@router.post("/session/start", response_model=StartSessionResponse)
async def start_session(request: Request):
    try:
        raw = await request.json()
    except Exception:
        raw = {}

    if isinstance(raw, dict) and "input" in raw and isinstance(raw["input"], dict):
        raw = raw["input"]

    try:
        payload = SessionRequest.model_validate(raw)
    except Exception:
        from datetime import datetime, UTC
        today = datetime.now(UTC).date().isoformat()
        payload = SessionRequest.model_validate({
            "user_id": "demo",
            "user_state": {"avatar": "reflecto", "date": today},
            "history": [
                {
                    "date": today,
                    "energy": 5,
                    "mood": 5,
                    "stress": 5,
                    "focus": 5,
                    "meaning": 5,
                }
            ],
            "flow_context": {},
            "raw_response": None,
        })

    if not payload.user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    result = create_session(
        user_id=payload.user_id,
        input_data=payload.model_dump(),
    )
    return {"session_id": result["session_id"], "status": "started"}
