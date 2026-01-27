from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class Presence(BaseModel):
    state: Literal["AWAKE", "CALM", "SLEEPING"]
    energy: Literal["low", "medium", "high"]
    focus: int  # 0–100
    mood: int   # 0–100
    time_of_day: Literal["morning", "afternoon", "evening", "night"]
    ts: datetime
