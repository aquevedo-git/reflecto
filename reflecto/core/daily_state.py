from dataclasses import dataclass, field, asdict
from datetime import date as dt_date
from typing import Optional, Dict, Any

@dataclass
class DailyState:
    date: str = field(default_factory=lambda: dt_date.today().isoformat())
    energy: int = 5
    mood: int = 5
    stress: int = 5
    focus: int = 5
    confidence: int = 5
    body: int = 5
    meaning: int = 5
    optional_topic: Optional[str] = None
    optional_text: Optional[str] = None

    def __post_init__(self):
        for field_name in ["energy", "mood", "stress", "focus", "confidence", "body", "meaning"]:
            value = getattr(self, field_name)
            if not isinstance(value, int) or not (1 <= value <= 10):
                raise ValueError(f"{field_name} must be an integer between 1 and 10.")
        if self.optional_topic is not None and not isinstance(self.optional_topic, str):
            raise ValueError("optional_topic must be a string or None.")
        if self.optional_text is not None and not isinstance(self.optional_text, str):
            raise ValueError("optional_text must be a string or None.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DailyState":
        return cls(**data)
