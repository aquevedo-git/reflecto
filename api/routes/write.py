from fastapi import APIRouter, Query
from api.contracts.write import ActionWrite
from api.services.action_store import add_action
import re
import openai
import os

router = APIRouter(prefix="/write")

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
    "worried": 3
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def get_mood_score_from_ai(note):
    if not OPENAI_API_KEY:
        return None
    openai.api_key = OPENAI_API_KEY
    prompt = f"Assign a mood score from 1 (very negative) to 10 (very positive) for the following statement: '{note}'. Respond with only the number."
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0.0
        )
        score_str = response.choices[0].message.content.strip()
        score = int(re.search(r"\d+", score_str).group())
        return score
    except Exception:
        return None

@router.post("/action")
async def write_action(
    action: ActionWrite,
    session_id: str = Query("demo")
):
    # If note is present and value is not, try to assign mood score
    if action.note and action.value is None:
        note_lower = action.note.lower()
        for word, score in MOOD_KEYWORDS.items():
            if re.search(rf"\\b{word}\\b", note_lower):
                action.value = score
                break
        # If user entered a number, use it as mood score
        num_match = re.search(r"\\b(\d{1,2})\\b", note_lower)
        if num_match:
            action.value = int(num_match.group(1))
        # If no score found, use AI
        if action.value is None:
            ai_score = await get_mood_score_from_ai(action.note)
            if ai_score:
                action.value = ai_score
    count = add_action(session_id, action)
    return {
        "status": "accepted",
        "count": count,
        "session_id": session_id,
        "assigned_value": action.value
    }
