from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class DailyStateInput(BaseModel):
    date: str
    energy: int
    mood: int
    stress: int
    focus: int
    meaning: int

class SessionRequest(BaseModel):
    user_id: str
    user_state: Dict[str, Any]
    history: List[DailyStateInput]
    flow_context: Dict[str, Any]
    raw_response: Optional[str] = None

class SessionResponse(BaseModel):
    avatar_prompt: Optional[str]
    questions: List[str]
    response: Optional[str]
    presence: Dict[str, Any]
    continuity_phrase: Optional[str]
    closing_phrase: Optional[str]
    meta: Dict[str, Any]
