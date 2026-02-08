"""Chatbot questions for Reflecto daily reflection."""

from typing import List, Optional, Dict, Any


def get_today_questions(
    previous_state: Optional[Dict[str, Any]],
    today_state: Optional[Dict[str, Any]],
    user_agrees_deep: bool = False
) -> List[str]:
    """
    Returns a list of plain text questions for today's reflection, following Reflecto's rules.
    previous_state: dict or None (yesterday's state)
    today_state: dict or None (today's answers so far)
    user_agrees_deep: bool, whether user has agreed to a deep question
    """
    daily_questions = [
        "How does your energy feel right now?",
        "What kind of mood are you noticing today?",
        "Is anything weighing on you today?",
        "How is your focus feeling at the moment?",
        "Do you feel steady or uncertain right now?"
    ]
    deep_questions = [
        "Is there something meaningful on your mind today?",
        "Would you like to gently reflect on something deeper?",
        "Is there a challenge you’d like to sit with for a moment?"
    ]

    questions = [daily_questions[0], daily_questions[1]]

    energy_val = None
    if today_state and 'energy' in today_state:
        try:
            energy_val = int(today_state['energy'])
        except Exception:
            pass
    if energy_val is not None and energy_val <= 3:
        return questions

    for q in daily_questions[2:]:
        if len(questions) < 5:
            questions.append(q)

    if user_agrees_deep:
        questions.append(deep_questions[0])

    return questions
