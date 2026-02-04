# reflecto/core/identity_outputs.py
from __future__ import annotations
from typing import Dict, List, Any

def build_identity_insight(identity: Dict[str, Any]) -> str:
    moods = identity.get("recurring_moods", [])
    stressors = identity.get("recurring_stressors", [])
    focus_patterns = identity.get("recurring_focus_patterns", [])
    themes = identity.get("recurring_themes", [])

    parts = []
    if moods:
        parts.append(f"Recurring mood: {', '.join(moods[:3])}.")
    if stressors:
        parts.append(f"Recurring stressor(s): {', '.join(stressors[:3])}.")
    if focus_patterns:
        parts.append(f"Focus pattern: {', '.join(focus_patterns[:3])}.")
    if themes:
        parts.append(f"Theme(s): {', '.join(themes[:3])}.")

    if not parts:
        return "Identity is still forming. Keep logging; patterns will crystallize after a few days."
    return " ".join(parts)

def select_daily_questions(identity: Dict[str, Any], base_questions: List[str], k: int = 3) -> List[str]:
    """
    Deterministic, no-LLM selector: pick questions based on identity signals.
    """
    focus_patterns = set(identity.get("recurring_focus_patterns", []))
    stressors = set(identity.get("recurring_stressors", []))
    moods = set(identity.get("recurring_moods", []))

    boosted = []
    neutral = []

    for q in base_questions:
        q_l = q.lower()
        score = 0

        # simple keyword boosts (extend later)
        if "focus" in q_l and ("high_focus_baseline" in focus_patterns):
            score += 2
        if "stress" in q_l and stressors:
            score += 2
        if "energy" in q_l and ("dormant" in moods or "low" in q_l):
            score += 1
        if "tomorrow" in q_l and stressors:
            score += 1

        (boosted if score > 0 else neutral).append((score, q))

    boosted.sort(key=lambda x: x[0], reverse=True)
    picked = [q for _, q in boosted[:k]]

    # fill remaining with first neutrals
    if len(picked) < k:
        picked.extend([q for _, q in neutral[: (k - len(picked))]])

    return picked[:k]

def apply_identity_to_avatar_state(identity: Dict[str, Any], avatar_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Light-touch behavior wiring. Do NOT override core state logic.
    """
    moods = set(identity.get("recurring_moods", []))
    stressors = set(identity.get("recurring_stressors", []))

    # Example: if identity shows low activity cycles, nudge "mood" only if currently dormant
    if "low_activity_cycles" in stressors and avatar_state.get("mood") == "dormant":
        avatar_state = dict(avatar_state)
        avatar_state["mood"] = "low_energy"

    # Example: if consistently high focus baseline, keep a hint field (non-breaking)
    if "high_focus_baseline" in set(identity.get("recurring_focus_patterns", [])):
        avatar_state = dict(avatar_state)
        avatar_state["tags"] = sorted(set(avatar_state.get("tags", [])) | {"high_focus"})

    return avatar_state
