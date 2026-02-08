"""
Phase 9: Session Runner for Reflecto

Provides a simple, human-facing wrapper for running a Reflecto session.
"""
from typing import Optional, Dict, Any, List
from domain.core.daily_state import DailyState
import reflecto.orchestrator


def run_session(
    user_state: dict,
    history: list[DailyState],
    flow_context: dict,
    raw_response: Optional[str] = None
) -> dict:
    """
    Calls run_reflecto() and returns a clean, human-facing output.
    Adapter only: no logic, no mutation, no recomputation.
    """
    orchestrator_output = reflecto.orchestrator.run_reflecto(
        user_state,
        history,
        flow_context,
        raw_response
    )
    if isinstance(orchestrator_output, dict) and "prompt" in orchestrator_output:
        shaped = orchestrator_output.get("shaped_response")
        closing = orchestrator_output.get("closing")
        continuity = orchestrator_output.get("continuity")

        closing_phrase = None
        if isinstance(closing, dict):
            closing_phrase = closing.get("closing_phrase")
        elif isinstance(closing, str):
            closing_phrase = closing

        continuity_phrase = None
        if isinstance(continuity, dict):
            continuity_phrase = continuity.get("recall_phrase") or continuity.get("continuity_phrase")
        elif isinstance(continuity, str):
            continuity_phrase = continuity

        response_text = shaped if shaped is not None else closing_phrase

        return {
            "avatar_prompt": orchestrator_output.get("prompt"),
            "questions": orchestrator_output.get("questions", []),
            "response": response_text,
            "presence": orchestrator_output.get("presence", {}),
            "continuity_phrase": continuity_phrase,
            "closing_phrase": closing_phrase,
            "meta": {
                "paused": orchestrator_output.get("paused", False),
                "closed": orchestrator_output.get("closed", False),
                "voice": orchestrator_output.get("voice"),
            }
        }

    closing_phrase = orchestrator_output.get("closing_phrase")
    if isinstance(closing_phrase, dict):
        closing_phrase = closing_phrase.get("closing_phrase")

    continuity_phrase = orchestrator_output.get("continuity_phrase")
    if isinstance(continuity_phrase, dict):
        continuity_phrase = continuity_phrase.get("recall_phrase") or continuity_phrase.get("continuity_phrase")

    response_text = orchestrator_output.get("response")
    if isinstance(response_text, dict):
        response_text = response_text.get("text")

    return {
        "avatar_prompt": orchestrator_output.get("avatar_prompt"),
        "questions": orchestrator_output.get("questions", []),
        "response": response_text,
        "presence": orchestrator_output.get("presence", {}),
        "continuity_phrase": continuity_phrase,
        "closing_phrase": closing_phrase,
        "meta": {
            "paused": orchestrator_output.get("paused", False),
            "closed": orchestrator_output.get("closed", False),
            "voice": orchestrator_output.get("voice"),
        }
    }
