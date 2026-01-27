# reflecto/avatar/evolution.py

from typing import Dict, Any

def derive_avatar_state(prev: Dict[str, Any] | None, snapshot: Dict[str, Any], streak: int, day: str) -> Dict[str, Any]:
    """
    Deterministic avatar evolution (v1).
    Same inputs => same outputs.
    """
    prev = prev or {}

    meaningful = int(snapshot.get("meaningful_events", 0))
    skills = snapshot.get("skills", {}) or {}

    # Simple v1 mood logic (tweak later)
    if meaningful == 0:
        mood = "dormant"
    elif streak >= 14:
        mood = "radiant"
    elif streak >= 7:
        mood = "confident"
    elif streak >= 3:
        mood = "steady"
    else:
        mood = "curious"

    state = {
        "version": "v1",
        "day": day,
        "mood": mood,
        "streak": streak,
        "meaningful_events": meaningful,
        "skills": skills,
        # keep a tiny continuity marker
        "last_presence": snapshot.get("last_presence"),
        "last_time_of_day": snapshot.get("last_time_of_day"),
    }

    # Optional: preserve stable identity-ish fields if present
    if "name" in prev:
        state["name"] = prev["name"]

    return state
