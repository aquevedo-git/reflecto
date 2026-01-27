from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class ActionWrite(BaseModel):
    type: Literal[
        "check_in",
        "log_mood",
        "log_focus",
        "log_health",
        "log_financial"
    ]
    value: Optional[int] = None
    note: Optional[str] = None
    ts: datetime
