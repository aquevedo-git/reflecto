"""
Voice Engine for Reflecto (Phase 6)

This module provides a pure, deterministic function to adjust the delivery (voice/tone) of a shaped response, without changing its meaning or content.
"""
from copy import deepcopy
from typing import Dict

def apply_voice(
    text: str,
    presence: Dict,
    silence: Dict,
    continuity: Dict
) -> Dict:
    """
    Adjusts the delivery of a message based on presence, silence, and continuity.
    Returns a dict with selected voice, adjusted text, and notes.
    
    Rules (priority order):
    1. If silence["should_close"] is True:
        - voice = "minimal"
        - remove extra sentence spacing
        - slightly shorter phrasing (but same meaning)
    2. If presence["emotional_tone"] == "warm":
        - voice = "soft"
        - add gentle cadence (commas, pauses)
        - soften edges
    3. If presence["energy_level"] == "low":
        - voice = "grounded"
        - slower rhythm, fewer clauses
    4. Else:
        - voice = "steady"
        - neutral, calm delivery
    """
    # Defensive copy (do not mutate input)
    original_text = text
    out_text = text
    notes = []
    voice = "steady"

    # 1. Minimal (should_close)
    if silence.get("should_close") is True:
        voice = "minimal"
        # Remove extra spaces, condense
        out_text = ' '.join(out_text.split())
        # Shorten delivery: remove softeners, keep meaning
        if out_text.endswith('.') and len(out_text.split('.')) > 1:
            # Remove trailing softener if present
            parts = [p.strip() for p in out_text.split('.') if p.strip()]
            if len(parts) > 1 and len(parts[-1].split()) <= 5:
                out_text = '. '.join(parts[:-1]) + '.'
        notes.append("Minimal: condensed, direct phrasing.")
        return {"voice": voice, "text": out_text, "notes": ' '.join(notes)}

    # 2. Soft (warm emotional tone)
    if presence.get("emotional_tone") == "warm":
        voice = "soft"
        # Add gentle cadence: insert commas/pauses after first clause
        sentences = [s.strip() for s in out_text.split('.') if s.strip()]
        if sentences:
            # Add a gentle pause after the first clause
            first = sentences[0]
            rest = '. '.join(sentences[1:])
            if ',' not in first and len(first.split()) > 4:
                first = first[:first.find(' ', len(first)//2)] + ', ' + first[first.find(' ', len(first)//2)+1:]
            out_text = first + ('. ' + rest if rest else '')
        # Soften edges: add gentle closer if not present
        if not out_text.endswith(' Take care.'):
            out_text = out_text.rstrip('.') + '. Take care.'
        notes.append("Soft: gentle cadence, softened edges.")
        return {"voice": voice, "text": out_text, "notes": ' '.join(notes)}

    # 3. Grounded (low energy)
    if presence.get("energy_level") == "low":
        voice = "grounded"
        # Slower rhythm: break into shorter sentences
        if ',' in out_text:
            out_text = out_text.replace(',', '.').replace('..', '.')
        # Fewer clauses: split long sentences
        sentences = [s.strip() for s in out_text.split('.') if s.strip()]
        out_text = '. '.join(sentences) + '.'
        notes.append("Grounded: slower rhythm, fewer clauses.")
        return {"voice": voice, "text": out_text, "notes": ' '.join(notes)}

    # 4. Steady (default)
    notes.append("Steady: neutral, calm delivery.")
    return {"voice": voice, "text": out_text, "notes": ' '.join(notes)}
