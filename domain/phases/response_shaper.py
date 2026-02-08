"""
Phase 4B — Response Shaping Engine
Shapes HOW Reflecto speaks, not WHAT it says.
"""
from typing import Dict
from domain.phases.purity import phase_pure


@phase_pure
def shape_response(raw_text: str, presence: Dict) -> str:
    """
    Adjusts the expression of raw_text based on the presence descriptor.
    Deterministic, reversible, no side effects.
    """
    text = raw_text
    tone = presence.get('emotional_tone', 'neutral')
    energy = presence.get('energy_level', 'medium')
    pacing = presence.get('pacing', 'normal')
    style = presence.get('presence_style', 'open')

    orig_endswith_period = raw_text.strip().endswith('.')
    if energy == 'low':
        parts = raw_text.split('. ')
        if len(parts) > 1:
            first = parts[0].strip()
            rest = '. '.join(parts[1:]).strip()
            if rest and not rest.endswith('.'):
                rest += '.'
            text = first + '.\n\n' + rest
        else:
            text = raw_text.strip()
    elif energy == 'high':
        parts = raw_text.split('. ')
        text = ' — '.join([p.strip() for p in parts])
        if orig_endswith_period and not text.endswith('.'):
            text += '.'

    if pacing == 'slow' and energy == 'medium':
        text = text.replace('. ', '.\n')
    elif pacing == 'spacious' and energy == 'medium':
        text = text.replace('. ', '.\n\n')

    if tone == 'warm':
        import re
        text = re.sub(r'\bYou\b', 'You — and that matters', text, count=1)
    elif tone == 'steady':
        text = text.replace('It sounds like', 'It seems')
    elif tone == 'grounded':
        text = text.replace('It sounds like', 'Here is what I notice:')

    if style == 'contained' and energy == 'medium':
        text = text.replace('. ', '.\n')
    elif style == 'open':
        text = text.replace('I notice', 'We notice')

    text = text.replace('..', '.')
    return text.strip()
