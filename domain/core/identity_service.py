from typing import Dict, Any

def normalize_identity(identity: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Pure helper: ensure identity has expected keys with defaults.
    """
    base = {
        "recurring_moods": [],
        "recurring_stressors": [],
        "recurring_focus_patterns": [],
        "recurring_themes": []
    }
    if identity:
        base.update(identity)
    return base


def update_identity(identity: Dict[str, Any] | None, patterns: dict) -> dict:
    """
    Phase D.1 identity update: overwrite identity fields from patterns.
    Pure, deterministic, no I/O.
    """
    identity = normalize_identity(identity)
    for k in sorted(patterns.keys()):
        identity[k] = patterns[k]
    return identity

