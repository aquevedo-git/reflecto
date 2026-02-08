from fastapi import APIRouter, Path
from api.contracts.write import ActionWrite
from api.services.action_store import add_action

router = APIRouter()

@router.post("/session/{session_id}/action")
async def session_scoped_action(
    session_id: str = Path(..., description="Session ID"),
    action: ActionWrite = ...
):
    # Pass action to domain runner (add_action)
    count = add_action(session_id, action)
    return {
        "status": "accepted",
        "count": count,
        "session_id": session_id,
        "assigned_value": action.value
    }
