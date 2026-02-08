from domain.core.snapshot_builder import build_daily_snapshot
from typing import List, Dict, Any


def build_daily_snapshot_from_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Pure snapshot builder from events. No persistence.
    """
    return build_daily_snapshot(events)
