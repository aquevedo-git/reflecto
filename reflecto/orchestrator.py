"""
Reflecto Orchestrator (Phase 8)

This module glues Phases 1–7 into a single deterministic call.
Strictly sequencing, no logic, no mutation, no I/O.
"""
from reflecto.avatar.generator import load_avatar_prompt
from reflecto.chatbot.flow import run_reflecto_flow
from reflecto.core.memory_intelligence import analyze_memory_patterns
from reflecto.avatar.presence_engine import build_presence
from reflecto.avatar.response_shaper import shape_response
from reflecto.avatar.silence_engine import decide_silence
from reflecto.avatar.continuity_engine import decide_continuity
from reflecto.avatar.voice_engine import apply_voice
from reflecto.avatar.closing_engine import decide_closing

def run_reflecto(
    user_state: dict,
    history: list,
    flow_context: dict,
    raw_response: str | None = None
) -> dict:
    """
    Runs Reflecto end-to-end using Phases 1–7.
    Returns a single structured result dict.
    """
    # Phase 1: Avatar prompt
    prompt = load_avatar_prompt(user_state["avatar"])

    # Phase 2: Flow (questions & decisions)
    flow_output = run_reflecto_flow(user_state, lambda q: "<stub>")
    questions = flow_output.get("questions", []) if isinstance(flow_output, dict) else []
    flow_decisions = flow_output.get("flow_decisions", []) if isinstance(flow_output, dict) else []

    # Phase 3: Memory intelligence
    memory_patterns = analyze_memory_patterns([vars(day) for day in history])

    # Phase 4A: Presence
    today_state = history[-1] if history else None
    presence = build_presence(today_state, memory_patterns, flow_context)

    # Phase 4B: Response shaping (optional)
    shaped_response = None
    if raw_response is not None:
        shaped_response = shape_response(raw_response, presence)

    # Phase 4C: Silence
    silence = decide_silence(presence, memory_patterns, flow_context)

    # Phase 5: Continuity
    continuity = decide_continuity(memory_patterns, presence, silence, flow_context)

    # Phase 6: Voice selection
    voice = apply_voice(
        shaped_response if shaped_response is not None else "",
        presence,
        silence,
        continuity
    )

    # Phase 7: Closing rituals
    closing = decide_closing(
        presence,
        silence,
        continuity,
        voice,
        flow_context
    )

    return {
        "prompt": prompt,
        "questions": questions,
        "flow_decisions": flow_decisions,
        "memory_patterns": memory_patterns,
        "presence": presence,
        "shaped_response": shaped_response,
        "silence": silence,
        "continuity": continuity,
        "voice": voice,
        "closing": closing
    }
