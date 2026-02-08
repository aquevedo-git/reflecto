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


def save_identity(user_id: str, identity: Dict[str, Any]) -> None:
    path = _identity_path(user_id)
    path.write_text(json.dumps(identity, indent=2))
