"""
Phase 4B — Response Shaping Engine
Shapes HOW Reflecto speaks, not WHAT it says.
"""
from typing import Dict

def shape_response(raw_text: str, presence: Dict) -> str:
    """
    Adjusts the expression of raw_text based on the presence descriptor.
    Deterministic, reversible, no side effects.
    """
    text = raw_text
    # Extract presence fields with defaults
    tone = presence.get('emotional_tone', 'neutral')
    energy = presence.get('energy_level', 'medium')
    pacing = presence.get('pacing', 'normal')
    style = presence.get('presence_style', 'open')

    # --- ENERGY ---
    orig_endswith_period = raw_text.strip().endswith('.')
    if energy == 'low':
        # Split into sentences, join with double newline, preserve periods
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
        # Join sentences with em dash, preserve period at end
        parts = raw_text.split('. ')
        text = ' — '.join([p.strip() for p in parts])
        if orig_endswith_period and not text.endswith('.'):
            text += '.'
    elif energy == 'medium':
        # Default: keep as is
        pass

    # --- PACING ---
    if pacing == 'slow' and energy == 'medium':
        # Only apply if not already split by energy
        text = text.replace('. ', '.\n')
    elif pacing == 'spacious' and energy == 'medium':
        text = text.replace('. ', '.\n\n')

    # --- TONE ---
    if tone == 'warm':
        # Insert ' — and that matters' after 'You' (first occurrence, with correct spacing)
        import re
        text = re.sub(r'\bYou\b', 'You — and that matters', text, count=1)
    elif tone == 'steady':
        text = text.replace('It sounds like', 'It seems')
    elif tone == 'grounded':
        text = text.replace('It sounds like', 'Here is what I notice:')

    # --- STYLE ---
    if style == 'contained' and energy == 'medium':
        # Fewer words, more silence (split sentences)
        text = text.replace('. ', '.\n')
    elif style == 'open':
        # Inclusive language
        text = text.replace('I notice', 'We notice')

    # Remove accidental double periods
    text = text.replace('..', '.')
    # Remove trailing whitespace
    return text.strip()
