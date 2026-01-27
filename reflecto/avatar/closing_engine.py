"""
Phase 7: Closing Rituals Engine for Reflecto

This module provides a pure, deterministic function for deciding when and how to gently close an interaction.
"""

def decide_closing(
    presence: dict,
    silence: dict,
    continuity: dict,
    voice: dict,
    flow_context: dict
) -> dict:
    """
    Returns a closing descriptor:
    {
        "should_close": bool,
        "closing_style": "gentle" | "warm" | "neutral" | "none",
        "closing_phrase": str | None,
        "notes": str
    }
    """
    # Do not mutate inputs
    should_close = False
    closing_style = "none"
    closing_phrase = None
    notes = ""

    # Rule 1: If silence.should_close is True → close
    if silence.get("should_close") is True:
        should_close = True
        notes = "Closure triggered by silence descriptor."
    # Rule 2: If user answered many questions → consider close
    elif flow_context.get("questions_asked", 0) >= 4:
        should_close = True
        notes = "Closure triggered by number of questions."

    # Decide style
    tone = voice.get("voice") or presence.get("tone") or "neutral"
    if should_close:
        if tone in ("warm", "caring", "gentle", "soft"):
            closing_style = "warm"
        elif tone in ("neutral", "steady", "even"):
            closing_style = "gentle"
        else:
            closing_style = "gentle"

        # Shorter close if energy is low
        energy = presence.get("energy")
        if energy is not None and energy <= 4:
            if closing_style == "warm":
                closing_phrase = "We can leave this here for today."
            else:
                closing_phrase = "It’s okay to stop here."
        else:
            if closing_style == "warm":
                closing_phrase = "We don’t have to do more right now."
            else:
                closing_phrase = "We can come back to this when you’re ready."
    else:
        closing_style = "none"
        closing_phrase = None
        notes = notes or "No closure triggered."

    return {
        "should_close": should_close,
        "closing_style": closing_style,
        "closing_phrase": closing_phrase,
        "notes": notes
    }
