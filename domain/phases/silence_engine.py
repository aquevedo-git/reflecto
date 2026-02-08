"""
Phase 4C — Silence, Timing & Pauses
Pure decision function for silence and closure.
"""
from copy import deepcopy
from domain.phases.purity import phase_pure


@phase_pure
def decide_silence(presence: dict, memory_patterns, flow_context: dict) -> dict:
    """
    Returns a silence descriptor:
    {
        "should_pause": bool,
        "pause_type": "short" | "long" | "none",
        "should_close": bool,
        "closure_style": "gentle" | "warm" | "none",
        "notes": str
    }
    """
    presence = deepcopy(presence)
    memory_patterns = deepcopy(memory_patterns)
    flow_context = deepcopy(flow_context)

    should_pause = False
    pause_type = "none"
    should_close = False
    closure_style = "none"
    notes = []

    energy = presence.get("energy")
    if energy is not None and energy <= 5:
        should_pause = True
        notes.append("Low energy triggers pause.")
    stress = presence.get("stress")
    if stress is not None and stress >= 7:
        should_pause = True
        notes.append("High stress triggers pause.")
    meaning_trend = memory_patterns.get("meaning_trend") if isinstance(memory_patterns, dict) else None
    if meaning_trend == "declining":
        should_pause = True
        notes.append("Declining meaning trend triggers pause.")

    pacing = presence.get("pacing", "steady")
    tone = presence.get("tone", "neutral")
    if should_pause:
        if pacing == "slow":
            pause_type = "long"
            notes.append("Slow pacing → long pause.")
        elif tone == "warm":
            pause_type = "short"
            notes.append("Warm tone → short pause.")
        else:
            pause_type = "long"
            notes.append("Default to long pause.")

    questions_asked = flow_context.get("questions_asked")
    if questions_asked is not None and questions_asked >= 6:
        should_close = True
        closure_style = "gentle"
        notes.append("Many questions answered → gentle closure.")
    if should_close and tone == "warm":
        closure_style = "warm"
        notes.append("Warm tone → warm closure.")

    return {
        "should_pause": should_pause,
        "pause_type": pause_type,
        "should_close": should_close,
        "closure_style": closure_style,
        "notes": " ".join(notes)
    }


build_silence = decide_silence
