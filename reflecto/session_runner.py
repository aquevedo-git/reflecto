"""
Phase 9: Session Runner for Reflecto

Provides a simple, human-facing wrapper for running a Reflecto session.
"""
from typing import Optional, Dict, Any, List
from reflecto.core.daily_state import DailyState
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
    return {
        "avatar_prompt": orchestrator_output.get("avatar_prompt"),
        "questions": orchestrator_output.get("questions", []),
        "response": orchestrator_output.get("response"),
        "presence": orchestrator_output.get("presence", {}),
        "continuity_phrase": orchestrator_output.get("continuity_phrase"),
        "closing_phrase": orchestrator_output.get("closing_phrase"),
        "meta": {
            "paused": orchestrator_output.get("paused", False),
            "closed": orchestrator_output.get("closed", False),
            "voice": orchestrator_output.get("voice"),
        }
    }
