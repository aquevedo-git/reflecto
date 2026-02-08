import pytest
from domain.core.daily_state import DailyState

import pytest
from unittest.mock import patch

# Patch OpenAI before importing load_avatar_prompt
with patch("reflecto.avatar.generator.OpenAI"):
    from reflecto.avatar.generator import load_avatar_prompt
from reflecto.chatbot.questions import get_today_questions
from reflecto.chatbot.memory import update_memory
import datetime

# PHASE 1: Core tests

def test_daily_questions_generated():
    questions = get_today_questions(None, None)
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert all(isinstance(q, str) and q.strip() for q in questions)

def test_daily_state_creation():
    today = datetime.date.today().isoformat()
    state = DailyState(date=today, energy=7, mood=6, stress=5, focus=8, confidence=7, body=6, meaning=7)
    assert state.date == today
    assert state.energy == 7
    assert hasattr(state, 'energy')


def test_avatar_prompt_loads_real_content():
    user_state = {'user_id': 'test_user', 'energy': 5}
    content = load_avatar_prompt(user_state)
    assert isinstance(content, str)
    assert content.strip() != "[PLACEHOLDER]"
    assert len(content.strip()) > 10

def test_memory_updated_with_today_entry():
    old_memory = {"history": []}
    today_state = {"date": datetime.date.today().isoformat(), "energy": 7, "mood": 6, "stress": 5, "focus": 8, "confidence": 7, "body": 6, "meaning": 7}
    new_memory = update_memory(old_memory, today_state)
    assert "history" in new_memory
    assert today_state in new_memory["history"]
