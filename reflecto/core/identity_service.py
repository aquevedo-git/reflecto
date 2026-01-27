import json
from pathlib import Path
from typing import Dict, Any

def _identity_path(user_id: str) -> Path:
    return Path(f"reflecto/memory/{user_id}_identity.json")


def load_identity(user_id: str) -> Dict[str, Any]:
    path = _identity_path(user_id)

    if not path.exists():
        return {
            "recurring_moods": [],
            "recurring_stressors": [],
            "recurring_focus_patterns": [],
            "recurring_themes": []
        }

    return json.loads(path.read_text())


def save_identity(user_id: str, identity: Dict[str, Any]):
    path = _identity_path(user_id)
    path.write_text(json.dumps(identity, indent=2))

def update_identity(user_id: str, patterns: dict) -> dict:
    """
    Phase D.1 identity update: overwrite identity fields from patterns
    (simple, deterministic, no learning yet)
    """
    identity = load_identity(user_id)

    for k, v in patterns.items():
        identity[k] = v

    save_identity(user_id, identity)
    return identity

