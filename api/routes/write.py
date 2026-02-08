from fastapi import APIRouter, Query
from api.contracts.write import ActionWrite
from application.services.action_service import add_action
from application.services.mood_scoring_service import score_mood_from_note
from extensions.llm_bridge.openai_adapter import OpenAIAdapter
from interfaces.runtime.action_store_adapters import get_action_store

router = APIRouter(prefix="/write")

_LLM_BRIDGE = OpenAIAdapter()

@router.post("/action")
async def write_action(
    action: ActionWrite,
    session_id: str = Query("demo")
):
    # If note is present and value is not, try to assign mood score
    if action.note and action.value is None:
        action.value = await score_mood_from_note(action.note, llm_bridge=_LLM_BRIDGE)
    count = add_action(session_id, action, store=get_action_store())
    return {
        "status": "accepted",
        "count": count,
        "session_id": session_id,
        "assigned_value": action.value
    }
