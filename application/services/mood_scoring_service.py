from __future__ import annotations

import asyncio
import os
import re
from typing import Optional

from application.ports.llm_bridge import LLMBridgePort


MOOD_KEYWORDS = {
    "great": 8,
    "good": 7,
    "okay": 5,
    "fine": 6,
    "bad": 3,
    "sad": 2,
    "tired": 4,
    "stressed": 2,
    "happy": 8,
    "excellent": 9,
    "terrible": 1,
    "amazing": 9,
    "awful": 1,
    "calm": 7,
    "energized": 8,
    "angry": 2,
    "worried": 3,
}


def _clamp_score(score: int) -> int:
    return max(1, min(10, score))


async def score_mood_from_note(
    note: str,
    llm_bridge: Optional[LLMBridgePort] = None,
) -> Optional[int]:
    if not note:
        return None

    note_lower = note.lower()

    for word, score in MOOD_KEYWORDS.items():
        if re.search(rf"\b{re.escape(word)}\b", note_lower):
            return _clamp_score(score)

    num_match = re.search(r"\b(\d{1,2})\b", note_lower)
    if num_match:
        return _clamp_score(int(num_match.group(1)))

    if llm_bridge is None:
        return None

    if os.getenv("REFLECTO_DETERMINISTIC") == "1" and not getattr(llm_bridge, "DETERMINISTIC_SAFE", False):
        return None

    prompt = (
        "Assign a mood score from 1 (very negative) to 10 (very positive) for the following statement: "
        f"'{note}'. Respond with only the number."
    )

    response = await asyncio.to_thread(llm_bridge.generate, prompt)
    if not response:
        return None

    score_match = re.search(r"\d+", response)
    if not score_match:
        return None

    return _clamp_score(int(score_match.group(0)))
