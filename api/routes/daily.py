from fastapi import APIRouter
from persistence.session_repository import SessionRepository
from reflecto.core.daily_update import run_daily_update

router = APIRouter()
repo = SessionRepository()

@router.get("/daily/{user_id}/{day}")
def daily_update(user_id: str, day: str):
    return run_daily_update(user_id=user_id, day=day, repo=repo)
