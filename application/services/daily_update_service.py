from typing import Dict, Any, Optional

from infrastructure.persistence.session_repository import SessionRepository
from domain.core.daily_update import run_daily_update
from domain.core.snapshot_builder import build_daily_snapshot
from application.ports.identity_store import IdentityStorePort
from application.ports.prompt_store import PromptStorePort
from application.services.reflection_service import build_reflection_prompt


def run_daily_update_service(
    user_id: str,
    day: str,
    repo: Optional[SessionRepository] = None,
    identity_store: Optional[IdentityStorePort] = None,
    prompt_store: Optional[PromptStorePort] = None,
) -> Dict[str, Any]:
    if identity_store is None:
        raise ValueError("identity_store is required")
    if prompt_store is None:
        raise ValueError("prompt_store is required")
    repo = repo or SessionRepository()
    events = repo.get_events_for_user_day(user_id, day)

    today_snapshot = build_daily_snapshot(events)
    # Build the pure update payload (include today's snapshot for streak/patterns)
    daily_snapshots = [{"snapshot": today_snapshot}] + repo.list_daily_snapshots(user_id=user_id, limit=60)
    raw_snapshots = [{"snapshot": today_snapshot}] + repo.list_daily_snapshots(user_id=user_id, limit=13)

    prev = repo.get_avatar_state(user_id)
    prev_state = prev["state"] if prev else None

    identity = identity_store.load_identity(user_id)

    update = run_daily_update(
        day=day,
        events=events,
        daily_snapshots=daily_snapshots,
        raw_snapshots=raw_snapshots,
        prev_avatar_state=prev_state,
        identity=identity,
    )

    # Persist derived outputs
    repo.upsert_daily_snapshot(user_id, day, update["snapshot"])
    repo.upsert_avatar_state(user_id, update["avatar_state"], version="v1")
    identity_store.save_identity(user_id, update["identity"])

    reflection_prompt = build_reflection_prompt(
        snapshot=update["snapshot"],
        avatar_state=update["avatar_state"],
        prompt_store=prompt_store,
    )

    return {
        **update,
        "reflection_prompt": reflection_prompt,
    }
