# reflecto/core/pattern_engine.py

from collections import Counter
from typing import List, Dict, Any


def extract_patterns(daily_snapshots: List[dict]) -> Dict[str, Any]:
    """
    Analyze last N days and extract identity-level patterns.
    Deterministic. No LLM yet.
    """

    moods = []
    focus_levels = []
    meaningful_counts = []

    for s in daily_snapshots:
        snap = s["snapshot"]
        avatar = s.get("avatar_state") or {}

        if avatar.get("mood"):
            moods.append(avatar["mood"])

        meaningful_counts.append(int(snap.get("meaningful_events", 0)))

        skills = snap.get("skills", {})
        if skills:
            focus_levels.append(skills.get("focus", 0))

    patterns = {}

    # recurring moods
    if moods:
        counts = Counter(moods)
        common = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:2]
        patterns["recurring_moods"] = [m[0] for m in common]

    # stress heuristic (many zero days)
    zero_days = sum(1 for x in meaningful_counts if x == 0)
    if zero_days >= 3:
        patterns["recurring_stressors"] = ["low_activity_cycles"]

    # focus pattern
    if focus_levels:
        avg_focus = sum(focus_levels) / len(focus_levels)
        if avg_focus >= 80:
            patterns["recurring_focus_patterns"] = ["high_focus_baseline"]
        elif avg_focus <= 50:
            patterns["recurring_focus_patterns"] = ["low_focus_baseline"]

    # life themes (v1 heuristic)
    if sum(meaningful_counts) >= 10:
        patterns["recurring_themes"] = ["consistent_progress"]

    return patterns
