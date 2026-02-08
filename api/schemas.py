from pydantic import BaseModel, model_validator
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

    @model_validator(mode="after")
    def ensure_deterministic_date_source(self):
        user_state = self.user_state or {}
        history = self.history or []
        has_date_in_user_state = isinstance(user_state, dict) and "date" in user_state
        has_date_in_history = any(getattr(h, "date", None) for h in history)
        if not has_date_in_user_state and not has_date_in_history:
            raise ValueError("Deterministic date required: provide user_state.date or history[].date")
        return self

class SessionResponse(BaseModel):
    avatar_prompt: Optional[str]
    questions: List[str]
    response: Optional[str]
    presence: Dict[str, Any]
    continuity_phrase: Optional[str]
    closing_phrase: Optional[str]
    meta: Dict[str, Any]
