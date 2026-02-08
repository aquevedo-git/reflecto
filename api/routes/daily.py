from fastapi import APIRouter
from application.services.daily_update_service import run_daily_update_service
from interfaces.runtime.store_adapters import get_identity_store, get_prompt_store

router = APIRouter()

@router.get("/daily/{user_id}/{day}")
def daily_update(user_id: str, day: str):
    return run_daily_update_service(
        user_id=user_id,
        day=day,
        identity_store=get_identity_store(),
        prompt_store=get_prompt_store(),
    )
