from domain.core.daily_state import DailyState
from domain.phases.purity import phase_pure


@phase_pure
def build_presence(today_state: DailyState, memory_patterns, flow_context: dict) -> dict:
    """
    Build a presence descriptor for the avatar based on today's state, memory patterns, and flow context.
    Returns a dict with keys:
        - energy_level: 'low' | 'medium' | 'high'
        - emotional_tone: 'soft' | 'neutral' | 'steady'
        - presence_style: 'holding' | 'open' | 'grounded'
        - pacing: 'slow' | 'normal' | 'spacious'
        - expression: 'subtle' | 'neutral' | 'alert'
        - notes: short human-readable summary
    """
    if today_state is None:
        return {
            "energy_level": "medium",
            "emotional_tone": "neutral",
            "presence_style": "holding",
            "pacing": "normal",
            "expression": "neutral",
            "notes": "No daily state provided."
        }
    if today_state.energy <= 4:
        energy_level = 'low'
    elif today_state.energy >= 7:
        energy_level = 'high'
    else:
        energy_level = 'medium'

    if today_state.stress >= 7:
        emotional_tone = 'soft'
    elif today_state.mood >= 7:
        emotional_tone = 'steady'
    else:
        emotional_tone = 'neutral'

    if flow_context.get('main_mode') == 'closure':
        presence_style = 'grounded'
    elif flow_context.get('main_mode') == 'explore':
        presence_style = 'open'
    else:
        presence_style = 'holding'

    if energy_level == 'low':
        pacing = 'slow'
    elif getattr(memory_patterns, 'trend', None) == 'improving':
        pacing = 'spacious'
    else:
        pacing = 'normal'

    if today_state.stress <= 3:
        expression = 'alert'
    elif getattr(memory_patterns, 'stability', None) == 'stable':
        expression = 'neutral'
    else:
        expression = 'subtle'

    notes = f"Energy: {energy_level}, Tone: {emotional_tone}, Style: {presence_style}, Pacing: {pacing}, Expression: {expression}."

    return {
        "energy_level": energy_level,
        "emotional_tone": emotional_tone,
        "presence_style": presence_style,
        "pacing": pacing,
        "expression": expression,
        "notes": notes
    }
