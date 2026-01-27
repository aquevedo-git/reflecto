# reflecto/core/identity_update.py

from typing import Dict, Any
from reflecto.core.identity_service import load_identity, save_identity

DECAY = 0.95   # forget slowly
REINFORCE = 1.1  # strengthen patterns

from reflecto.core.identity_service import load_identity, save_identity
from reflecto.core.identity_crystallizer import crystallize

def update_identity_from_snapshot(user_id: str, snapshot: dict, day: str):
    identity = load_identity(user_id)
    patterns = snapshot.get("patterns", {})

    identity = crystallize(identity, patterns, day)
    save_identity(user_id, identity)

    return identity

