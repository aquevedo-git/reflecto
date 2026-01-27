import uuid
from datetime import datetime
from typing import Any

class SessionRecord:
    def __init__(self, user_id: str, data: dict, version: str):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.utcnow().isoformat()
        self.data = data
        self.version = version
