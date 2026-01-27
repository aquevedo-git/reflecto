from typing import Dict, Any

def validate_event(event_type: str, data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    return True

