from fastapi import APIRouter, Query
from api.contracts.write import ActionWrite
from api.services.action_store import add_action

router = APIRouter(prefix="/write")


@router.post("/action")
async def write_action(
    action: ActionWrite,
    session_id: str = Query("demo")
):
    count = add_action(session_id, action)

    return {
        "status": "accepted",
        "count": count,
        "session_id": session_id
    }
