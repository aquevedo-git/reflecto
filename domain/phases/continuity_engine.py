"""
Phase 5 — Continuity & Gentle Recall
Pure decision function for soft, human recall of past patterns.
"""
from typing import Dict, Any
from domain.phases.purity import phase_pure


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


@phase_pure
def decide_continuity(memory_patterns, presence: dict, silence: dict, flow_context: dict) -> dict:
    """
    Returns:
    {
        "should_recall": bool,
        "recall_style": "soft" | "gentle" | "none",
        "recall_phrase": str | None,
        "notes": str
    }
    """
    if _get(silence, "should_close") or _get(silence, "close_conversation"):
        return {
            "should_recall": False,
            "recall_style": "none",
            "recall_phrase": None,
            "notes": "Silence requested closure. No recall."
        }

    recall_phrase = None
    recall_style = "none"
    notes = []

    meaning_trend = _get(memory_patterns, "meaning_trend")
    if meaning_trend == "rising":
        recall_phrase = "There’s a gentle sense of meaning growing here."
        recall_style = "gentle"
        notes.append("Meaning trend rising → gentle recall.")
    elif _get(memory_patterns, "energy_trend") == "declining":
        recall_phrase = "If things feel a little heavier lately, that’s okay."
        recall_style = "soft"
        notes.append("Energy trend declining → soft reassurance.")
    elif _get(memory_patterns, "recurring_theme") or _get(memory_patterns, "recurring_themes"):
        recall_phrase = "This feels like something that’s been visiting you lately."
        recall_style = "gentle"
        notes.append("Recurring theme present → gentle recall.")
    else:
        recall_phrase = None
        recall_style = "none"
        notes.append("No recall-worthy pattern found.")

    return {
        "should_recall": recall_style != "none",
        "recall_style": recall_style,
        "recall_phrase": recall_phrase,
        "notes": "; ".join(notes)
    }


build_continuity = decide_continuity
