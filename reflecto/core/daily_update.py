# reflecto/core/daily_update.py

from persistence.session_repository import SessionRepository
from reflecto.core.snapshot_service import build_and_store_daily_snapshot
from reflecto.avatar.evolution import derive_avatar_state
from reflecto.core.streaks import compute_streak
from reflecto.core.reflection_service import build_daily_reflection
from reflecto.core.pattern_engine import extract_patterns
from reflecto.core.identity_service import update_identity
from reflecto.core.identity_update import update_identity_from_snapshot




def run_daily_update(user_id: str, day: str, repo: SessionRepository) -> dict:
    """
    C.3: build snapshot, compute streak, update avatar state,
    and build daily reflection prompt.
    """
    # 1. Build snapshot
    snapshot = build_and_store_daily_snapshot(user_id=user_id, day=day, repo=repo)
    identity = update_identity_from_snapshot(user_id, snapshot, day)



    # 2. Compute streak (newest -> oldest)
    snapshots = repo.list_daily_snapshots(user_id=user_id, limit=60)
    streak = compute_streak(snapshots)

    # 3. Evolve avatar
    prev = repo.get_avatar_state(user_id)
    prev_state = prev["state"] if prev else None

    avatar_state = derive_avatar_state(prev_state, snapshot, streak, day)
    repo.upsert_avatar_state(user_id, avatar_state, version="v1")

    raw_snapshots = repo.list_daily_snapshots(user_id=user_id, limit=14)
    avatar = repo.get_avatar_state(user_id)

    snapshots_for_patterns = [
        {
            "snapshot": s["snapshot"],
            "avatar_state": avatar["state"] if avatar else None
        }
        for s in raw_snapshots
    ]

    patterns = extract_patterns(snapshots_for_patterns)

    identity = update_identity_from_snapshot(user_id, snapshot, day)


    # 4. Build daily reflection prompt (FINAL C.3 STEP)
    reflection_prompt = build_daily_reflection(
    snapshot=snapshot,
    avatar_state=avatar_state,
)


    # 5. Return full daily payload
    return {
        "day": day,
        "snapshot": snapshot,
        "streak": streak,
        "avatar_state": avatar_state,
        "identity": identity,
        "reflection_prompt": reflection_prompt,
    }

