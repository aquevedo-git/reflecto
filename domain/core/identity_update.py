# reflecto/core/identity_update.py

from typing import Dict, Any
from domain.core.identity_crystallizer import crystallize

def update_identity_from_snapshot(identity: Dict[str, Any] | None, snapshot: dict, day: str, patterns: dict | None = None) -> dict:
    """
    Pure identity update: no I/O, no external state.
    """
    identity = identity or {}
    resolved_patterns = patterns if patterns is not None else snapshot.get("patterns", {})

    return crystallize(identity, resolved_patterns, day)

