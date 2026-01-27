from datetime import datetime
from api.contracts.presence import Presence
from api.contracts.write import ActionWrite

def derive_presence(
    actions: list[ActionWrite],
    now: datetime
) -> Presence:
    """
    Deterministic presence derivation.
    NO IO.
    NO randomness.
    NO side effects.
    """

    hour = now.hour
    if 5 <= hour < 12:
        time_of_day = "morning"
    elif 12 <= hour < 17:
        time_of_day = "afternoon"
    elif 17 <= hour < 22:
        time_of_day = "evening"
    else:
        time_of_day = "night"

    # Defaults
    energy = "medium"
    mood = 50
    focus = 50
    state = "AWAKE"

    # Simple rules (we’ll evolve these later)
    for a in actions[-10:]:
        if a.type == "log_focus" and a.value is not None:
            focus = a.value
        if a.type == "log_mood" and a.value is not None:
            mood = a.value

    if time_of_day == "night":
        state = "SLEEPING"
        energy = "low"
    elif mood < 40:
        state = "CALM"
        energy = "low"

    return Presence(
        state=state,
        energy=energy,
        focus=focus,
        mood=mood,
        time_of_day=time_of_day,
        ts=now
    )

# Presence is always derived from actions
# Never stored or mutated directly
