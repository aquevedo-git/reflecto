# reflecto/core/daily_update.py

from typing import Dict, Any, List
from domain.core.snapshot_builder import build_daily_snapshot
from domain.core.avatar_evolution import derive_avatar_state
from domain.core.streaks import compute_streak
from domain.core.pattern_engine import extract_patterns
from domain.core.identity_update import update_identity_from_snapshot


def run_daily_update(
    day: str,
    events: List[Dict[str, Any]],
    daily_snapshots: List[Dict[str, Any]],
    raw_snapshots: List[Dict[str, Any]],
    prev_avatar_state: Dict[str, Any] | None,
    identity: Dict[str, Any] | None,
) -> dict:
    """
    Pure daily update computation. No persistence, no I/O.
    """

    snapshot = build_daily_snapshot(events)
    streak = compute_streak(daily_snapshots)

    avatar_state = derive_avatar_state(prev_avatar_state, snapshot, streak, day)

    snapshots_for_patterns = [
        {
            "snapshot": s["snapshot"],
            "avatar_state": avatar_state,
        }
        for s in raw_snapshots
    ]

    patterns = extract_patterns(snapshots_for_patterns)
    identity = update_identity_from_snapshot(identity, snapshot, day, patterns=patterns)

    return {
        "day": day,
        "snapshot": snapshot,
        "streak": streak,
        "avatar_state": avatar_state,
        "patterns": patterns,
        "identity": identity,
    }
