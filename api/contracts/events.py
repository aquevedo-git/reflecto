# api/contracts/events.py

from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class SessionEvent(BaseModel):
    id: str
    session_id: str
    timestamp: datetime
    type: str
    payload: Dict[str, Any]
    source: str
