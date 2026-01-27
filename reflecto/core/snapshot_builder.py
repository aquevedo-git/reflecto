# reflecto/core/snapshot_builder.py

from typing import List, Dict, Any

DEFAULT_SKILLS = {
    "financial": 80,
    "health": 70,
    "focus": 90,
    "relationships": 60
}

MEANINGFUL_EVENT_TYPES = {
    "presence",
    "skills",
    "time_of_day",
    # later: mood, activity, reflection, etc
}


def build_daily_snapshot(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic daily snapshot builder (C.2 v1)
    Same events -> same snapshot (required for replay + trust)
    """

    snapshot = {
        "counts": {},                 # event counts by type
        "last_presence": None,         # final presence of day
        "last_time_of_day": None,      # final time_of_day
        "skills": DEFAULT_SKILLS.copy(),
        "meaningful_events": 0         # used for streaks
    }

    for e in events:
        t = e["type"]

        # count events
        snapshot["counts"][t] = snapshot["counts"].get(t, 0) + 1

        # capture final states
        if t == "presence":
            snapshot["last_presence"] = e["payload"]

        elif t == "time_of_day":
            snapshot["last_time_of_day"] = e["payload"].get("time_of_day")

        elif t == "skills":
            snapshot["skills"] = e["payload"]

        # streak signal
        if t in MEANINGFUL_EVENT_TYPES:
            snapshot["meaningful_events"] += 1

    return snapshot
