# reflecto/core/streaks.py

from typing import List, Dict

def compute_streak(daily_snapshots: List[Dict]) -> int:
    """
    daily_snapshots must be sorted newest → oldest.
    Streak = consecutive days with meaningful_events > 0.
    """
    streak = 0

    for s in daily_snapshots:
        if s["snapshot"].get("meaningful_events", 0) > 0:
            streak += 1
        else:
            break

    return streak
