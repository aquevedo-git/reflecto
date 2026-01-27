from reflecto.core.snapshot_builder import build_daily_snapshot
from persistence.session_repository import SessionRepository


def build_and_store_daily_snapshot(user_id: str, day: str, repo: SessionRepository) -> dict:
    events = repo.get_events_for_user_day(user_id, day)

    snapshot = build_daily_snapshot(events)

    repo.upsert_daily_snapshot(user_id, day, snapshot)
    return snapshot
