"""
Voice Engine for Reflecto (Phase 6)

This module provides a pure, deterministic function to adjust the delivery (voice/tone) of a shaped response, without changing its meaning or content.
"""
from typing import Dict
from domain.phases.purity import phase_pure


@phase_pure
def apply_voice(
    text: str,
    presence: Dict,
    silence: Dict,
    continuity: Dict
) -> Dict:
    """
    Adjusts the delivery of a message based on presence, silence, and continuity.
    Returns a dict with selected voice, adjusted text, and notes.
    """
    out_text = text
    notes = []
    voice = "steady"

    if silence.get("should_close") is True:
        voice = "minimal"
        out_text = ' '.join(out_text.split())
        if out_text.endswith('.') and len(out_text.split('.')) > 1:
            parts = [p.strip() for p in out_text.split('.') if p.strip()]
            if len(parts) > 1 and len(parts[-1].split()) <= 5:
                out_text = '. '.join(parts[:-1]) + '.'
        notes.append("Minimal: condensed, direct phrasing.")
        return {"voice": voice, "text": out_text, "notes": ' '.join(notes)}

    if presence.get("emotional_tone") == "warm":
        voice = "soft"
        sentences = [s.strip() for s in out_text.split('.') if s.strip()]
        if sentences:
            first = sentences[0]
            rest = '. '.join(sentences[1:])
            if ',' not in first and len(first.split()) > 4:
                first = first[:first.find(' ', len(first)//2)] + ', ' + first[first.find(' ', len(first)//2)+1:]
            out_text = first + ('. ' + rest if rest else '')
        if not out_text.endswith(' Take care.'):
            out_text = out_text.rstrip('.') + '. Take care.'
        notes.append("Soft: gentle cadence, softened edges.")
        return {"voice": voice, "text": out_text, "notes": ' '.join(notes)}

    if presence.get("energy_level") == "low":
        voice = "grounded"
        if ',' in out_text:
            out_text = out_text.replace(',', '.').replace('..', '.')
        sentences = [s.strip() for s in out_text.split('.') if s.strip()]
        out_text = '. '.join(sentences) + '.'
        notes.append("Grounded: slower rhythm, fewer clauses.")
        return {"voice": voice, "text": out_text, "notes": ' '.join(notes)}

    notes.append("Steady: neutral, calm delivery.")
    return {"voice": voice, "text": out_text, "notes": ' '.join(notes)}


build_voice = apply_voice
