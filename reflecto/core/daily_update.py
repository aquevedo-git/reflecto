# reflecto/core/daily_update.py

from persistence.session_repository import SessionRepository
from reflecto.core.snapshot_service import build_and_store_daily_snapshot
from reflecto.avatar.evolution import derive_avatar_state
from reflecto.core.streaks import compute_streak
from reflecto.core.reflection_service import build_daily_reflection
from reflecto.core.pattern_engine import extract_patterns
from reflecto.core.identity_update import update_identity_from_snapshot


def run_daily_update(user_id: str, day: str, repo: SessionRepository) -> dict:
    """
    D.3: build snapshot, compute streak, evolve avatar, extract patterns,
    update identity, build reflection prompt.
    """

    # 1) Build snapshot for the day
    snapshot = build_and_store_daily_snapshot(user_id=user_id, day=day, repo=repo)

    # 2) Compute streak (newest -> oldest)
    snapshots = repo.list_daily_snapshots(user_id=user_id, limit=60)
    streak = compute_streak(snapshots)

    # 3) Evolve avatar + persist
    prev = repo.get_avatar_state(user_id)
    prev_state = prev["state"] if prev else None

    avatar_state = derive_avatar_state(prev_state, snapshot, streak, day)
    repo.upsert_avatar_state(user_id, avatar_state, version="v1")

    # 4) Extract patterns from recent snapshots (last 14 days)
    raw_snapshots = repo.list_daily_snapshots(user_id=user_id, limit=14)

    snapshots_for_patterns = [
        {
            "snapshot": s["snapshot"],
            "avatar_state": avatar_state,  # we already have today's avatar state
        }
        for s in raw_snapshots
    ]

    patterns = extract_patterns(snapshots_for_patterns)

    # 5) Update identity (crystallization / evidence) using day
    # IMPORTANT: update_identity_from_snapshot should accept patterns or read them from snapshot.
    # We'll pass patterns explicitly if your function supports it.
    try:
        identity = update_identity_from_snapshot(user_id, snapshot, day, patterns=patterns)
    except TypeError:
        # fallback if your function signature is (user_id, snapshot, day)
        # in that case make sure snapshot includes patterns
        snapshot["patterns"] = patterns
        identity = update_identity_from_snapshot(user_id, snapshot, day)

    # 6) Build reflection prompt (now identity-aware if your reflection_service supports it)
    try:
        reflection_prompt = build_daily_reflection(
            snapshot=snapshot,
            avatar_state=avatar_state,
            identity=identity,
        )
    except TypeError:
        # fallback if build_daily_reflection only takes snapshot + avatar_state
        reflection_prompt = build_daily_reflection(
            snapshot=snapshot,
            avatar_state=avatar_state,
        )

    # 7) Return payload
    return {
        "day": day,
        "snapshot": snapshot,
        "streak": streak,
        "avatar_state": avatar_state,
        "patterns": patterns,
        "identity": identity,
        "reflection_prompt": reflection_prompt,
    }
