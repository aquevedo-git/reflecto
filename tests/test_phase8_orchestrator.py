"""
Tests for Phase 8 — Reflecto Orchestrator
"""
import copy
import pytest
from reflecto.orchestrator import run_reflecto
from reflecto.core.daily_state import DailyState

def make_fake_history():
    return [
        DailyState(
            date=f"2026-01-{20+i}",
            energy=6,
            mood=7,
            stress=4,
            focus=5,
            meaning=6
        ) for i in range(7)
    ]

def test_run_reflecto_determinism():
    user_state = {"user_id": "u", "name": "A", "avatar": "reflecto"}
    history = make_fake_history()
    flow_context = {"main_mode": "explore"}
    raw_response = "Today was tough."
    out1 = run_reflecto(copy.deepcopy(user_state), copy.deepcopy(history), copy.deepcopy(flow_context), raw_response)
    out2 = run_reflecto(copy.deepcopy(user_state), copy.deepcopy(history), copy.deepcopy(flow_context), raw_response)
    assert out1 == out2

def test_run_reflecto_output_shape():
    user_state = {"user_id": "u", "name": "A", "avatar": "reflecto"}
    history = make_fake_history()
    flow_context = {"main_mode": "explore"}
    out = run_reflecto(user_state, history, flow_context)
    keys = [
        "prompt", "questions", "flow_decisions", "memory_patterns", "presence",
        "shaped_response", "silence", "continuity", "voice", "closing"
    ]
    assert set(out.keys()) == set(keys)

def test_run_reflecto_all_phases_called(monkeypatch):
    calls = []
    import reflecto.orchestrator as orch
    monkeypatch.setattr(orch, "load_avatar_prompt", lambda *a, **k: calls.append("prompt") or "p")
    monkeypatch.setattr(orch, "run_reflecto_flow", lambda *a, **k: calls.append("flow") or {"questions": [], "flow_decisions": []})
    monkeypatch.setattr(orch, "analyze_memory_patterns", lambda *a, **k: calls.append("memory") or "m")
    monkeypatch.setattr(orch, "build_presence", lambda *a, **k: calls.append("presence") or "pr")
    monkeypatch.setattr(orch, "shape_response", lambda *a, **k: calls.append("shape") or "sr")
    monkeypatch.setattr(orch, "decide_silence", lambda *a, **k: calls.append("silence") or "si")
    monkeypatch.setattr(orch, "decide_continuity", lambda *a, **k: calls.append("continuity") or "co")
    monkeypatch.setattr(orch, "apply_voice", lambda *a, **k: calls.append("voice") or "v")
    monkeypatch.setattr(orch, "decide_closing", lambda *a, **k: calls.append("closing") or "cl")
    user_state = {"user_id": "u", "name": "A", "avatar": "reflecto"}
    history = make_fake_history()
    flow_context = {"main_mode": "explore"}
    orch.run_reflecto(user_state, history, flow_context, "hi")
    assert calls == [
        "prompt", "flow", "memory", "presence", "shape", "silence", "continuity", "voice", "closing"
    ]

def test_run_reflecto_skip_shape():
    user_state = {"user_id": "u", "name": "A", "avatar": "reflecto"}
    history = make_fake_history()
    flow_context = {"main_mode": "explore"}
    out = run_reflecto(user_state, history, flow_context)
    assert out["shaped_response"] is None

def test_run_reflecto_no_input_mutation():
    user_state = {"user_id": "u", "name": "A", "avatar": "reflecto"}
    history = make_fake_history()
    flow_context = {"main_mode": "explore"}
    user_state_orig = copy.deepcopy(user_state)
    history_orig = copy.deepcopy(history)
    flow_context_orig = copy.deepcopy(flow_context)
    run_reflecto(user_state, history, flow_context, "hi")
    assert user_state == user_state_orig
    assert history == history_orig
    assert flow_context == flow_context_orig
