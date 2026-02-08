from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.session_service import repo
from persistence.models import SessionRecord
import uuid

router = APIRouter()

class StartSessionResponse(BaseModel):
    session_id: str
    status: str


from fastapi import Request

@router.post("/session/start", response_model=StartSessionResponse)
async def start_session(request: Request):
    # Accept user_id from JSON body or default to 'anonymous'
    try:
        data = await request.json()
        user_id = data.get("user_id", "anonymous")
    except Exception:
        user_id = "anonymous"
    session_id = str(uuid.uuid4())
    record = SessionRecord(user_id=user_id, data={}, version="reflecto-v1.0")
    record.id = session_id  # override with deterministic id
    repo.save(record)
    return {"session_id": session_id, "status": "started"}
