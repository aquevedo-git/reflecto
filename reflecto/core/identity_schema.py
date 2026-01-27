# reflecto/core/identity_schema.py
from typing import Dict, Any

def empty_identity() -> Dict[str, Any]:
    return {
        "recurring_moods": [],
        "recurring_stressors": [],
        "recurring_focus_patterns": [],
        "recurring_themes": [],

        # Phase D.2 fields
        "confidence": {},
        "evidence": {},
        "last_updated": None
    }
