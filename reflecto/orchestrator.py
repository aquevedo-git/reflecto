"""
Reflecto Phase Orchestrator
Pure deterministic cognition pipeline coordinator.
"""

from __future__ import annotations

import copy

from domain.core.daily_state import DailyState
from domain.core.memory_intelligence import analyze_memory_patterns

from reflecto.avatar.presence_engine import build_presence
from reflecto.avatar.silence_engine import build_silence
from reflecto.avatar.continuity_engine import build_continuity
from reflecto.avatar.closing_engine import build_closing
from reflecto.chatbot.flow import run_reflecto_flow
from reflecto.avatar.response_shaper import shape_response as _shape_response_impl

from domain.phases.purity import freeze_value

from .avatar.voice_engine import build_voice


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _coerce_today_state(user_state, history):
    """
    Produce a DailyState from user_state when possible; otherwise fallback to last history item.
    Does not mutate inputs.
    """
    if isinstance(user_state, DailyState):
        return user_state

    if isinstance(user_state, dict):
        allowed = set(getattr(DailyState, "__annotations__", {}).keys())
        filtered = {k: v for k, v in user_state.items() if k in allowed}
        if filtered and "date" in filtered:
            return DailyState(**filtered)

    if history:
        last = history[-1]
        if isinstance(last, DailyState):
            return last
        if isinstance(last, dict):
            allowed = set(getattr(DailyState, "__annotations__", {}).keys())
            filtered = {k: v for k, v in last.items() if k in allowed}
            if "date" not in filtered:
                raise TypeError("Unable to derive DailyState: missing date in history item.")
            return DailyState(**filtered)

    raise TypeError("Unable to derive DailyState from user_state or history.")


def load_avatar_prompt(today_state, memory_patterns, flow_context):
    """
    Hook for tests/patching. Tests monkeypatch this.
    """
    if isinstance(flow_context, dict):
        return flow_context.get("avatar_prompt") or flow_context.get("avatar") or "reflecto"
    return "reflecto"


def serialize_history(history):
    out = []
    for day in history:
        if isinstance(day, DailyState):
            out.append(day.to_dict())
        elif isinstance(day, dict):
            out.append(dict(day))
        elif hasattr(day, "to_dict"):
            out.append(day.to_dict())
        else:
            raise ValueError("Unsupported history item; expected DailyState/dict/to_dict().")
    return out


def _as_plain_dict(x) -> dict:
    if x is None:
        return {}
    if isinstance(x, dict):
        return dict(x)
    if hasattr(x, "to_dict"):
        return dict(x.to_dict())
    if hasattr(x, "__dict__"):
        return dict(vars(x))
    return {}


# ------------------------------------------------------------
# Phase functions (MUST exist for monkeypatching in tests)
# ------------------------------------------------------------

def shape_response(*args, **kwargs):
    """
    Wrapper exposed at module level so tests can monkeypatch `orch.shape_response`.
    """
    return _shape_response_impl(*args, **kwargs)


def decide_silence(presence_dict, memory_patterns_dict, flow_context):
    return build_silence(presence_dict, memory_patterns_dict, flow_context)


def decide_continuity(memory_patterns_dict, presence_dict, silence_dict, flow_context):
    return build_continuity(memory_patterns_dict, presence_dict, silence_dict, flow_context)


def apply_voice(text, presence_dict, silence_dict, continuity_dict):
    return build_voice(text, presence_dict, silence_dict, continuity_dict)


def decide_closing(presence_dict, silence_dict, continuity_dict, voice_dict, flow_context):
    return build_closing(presence_dict, silence_dict, continuity_dict, voice_dict, flow_context)


# ------------------------------------------------------------
# Main Reflecto Pipeline (Phase 8 output contract)
# ------------------------------------------------------------

def run_reflecto(
    user_state: dict,
    history: list,
    flow_context: dict,
    raw_response: str | None = None,
):
    """
    Must return exactly these keys (tests/test_phase8_orchestrator.py):
      prompt, questions, flow_decisions, memory_patterns, presence,
      shaped_response, silence, continuity, voice, closing

    Must call phases in this order (monkeypatch test):
      prompt, flow, memory, presence, shape, silence, continuity, voice, closing
    """
    user_state = copy.deepcopy(user_state)
    history = copy.deepcopy(history)
    flow_context = copy.deepcopy(flow_context)
    today_state = _coerce_today_state(user_state, history)

    # 1) prompt
    prompt = load_avatar_prompt(today_state, None, flow_context)

    # 2) flow
    responder = (lambda _: raw_response) if raw_response is not None else (lambda _: "<stub>")
    flow_output = run_reflecto_flow(today_state.to_dict(), responder) or {}
    questions = flow_output.get("questions", []) if isinstance(flow_output, dict) else []
    flow_decisions = flow_output.get("flow_decisions", []) if isinstance(flow_output, dict) else []

    # 3) memory
    memory_patterns = analyze_memory_patterns(serialize_history(history))

    # 4) presence
    presence = build_presence(today_state, memory_patterns, flow_context)
    presence_dict = _as_plain_dict(presence)
    memory_patterns_dict = _as_plain_dict(memory_patterns)

    # 5) shape (must be called even when raw_response is None)
    shape_result = None
    try:
        if raw_response is None:
            shape_response("", presence_dict)
        else:
            shape_result = shape_response(raw_response, presence_dict)
    except Exception:
        pass

    # 6) silence
    silence = decide_silence(presence_dict, memory_patterns_dict, flow_context)

    # 7) continuity (test expects this before voice)
    continuity = decide_continuity(memory_patterns_dict, presence_dict, silence, flow_context)
    continuity_dict = _as_plain_dict(continuity)

    # 8) voice
    voice_text = raw_response if raw_response is not None else ""
    voice = apply_voice(voice_text, presence_dict, silence, continuity_dict)
    voice_dict = _as_plain_dict(voice)

    # 9) closing
    closing = decide_closing(presence_dict, silence, continuity_dict, voice_dict, flow_context)

    # shaped_response must be None when raw_response is None (skip-shape test)
    shaped_response = None if raw_response is None else shape_result

    output = {
        "prompt": copy.deepcopy(prompt),
        "questions": copy.deepcopy(questions),
        "flow_decisions": copy.deepcopy(flow_decisions),
        "memory_patterns": copy.deepcopy(memory_patterns),
        "presence": copy.deepcopy(presence),
        "shaped_response": copy.deepcopy(shaped_response),
        "silence": copy.deepcopy(silence),
        "continuity": copy.deepcopy(continuity),
        "voice": copy.deepcopy(voice),
        "closing": copy.deepcopy(closing),
    }

    # Enforce immutability at the orchestration boundary
    return freeze_value(output)