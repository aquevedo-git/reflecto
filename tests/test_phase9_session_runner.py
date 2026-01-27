import copy
import pytest
from reflecto.session_runner import run_session
from reflecto.core.daily_state import DailyState
from reflecto.orchestrator import run_reflecto

class DummyDailyState(DailyState):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@pytest.fixture
def fake_inputs():
    user_state = {'user_id': 'u1', 'name': 'Test', 'avatar': 'reflecto'}
    history = [
        DummyDailyState(date='2026-01-20', energy=7, mood=6, stress=4, focus=5, meaning=6),
        DummyDailyState(date='2026-01-21', energy=6, mood=7, stress=5, focus=4, meaning=7)
    ]
    flow_context = {'main_mode': 'explore'}
    raw_response = 'Sample raw response.'
    return user_state, history, flow_context, raw_response

def test_run_session_deterministic(monkeypatch, fake_inputs):
    user_state, history, flow_context, raw_response = fake_inputs
    # Patch orchestrator to return a known output
    expected = {
        "avatar_prompt": "Hi!",
        "questions": ["How are you?"],
        "response": "I'm here.",
        "presence": {"status": "present"},
        "continuity_phrase": "Let's continue.",
        "closing_phrase": "Goodbye!",
        "paused": False,
        "closed": True,
        "voice": "default"
    }
    def fake_run_reflecto(*args, **kwargs):
        return expected.copy()
    monkeypatch.setattr("reflecto.orchestrator.run_reflecto", fake_run_reflecto)
    out = run_session(user_state, history, flow_context, raw_response)
    assert out["avatar_prompt"] == "Hi!"
    assert out["questions"] == ["How are you?"]
    assert out["response"] == "I'm here."
    assert out["presence"] == {"status": "present"}
    assert out["continuity_phrase"] == "Let's continue."
    assert out["closing_phrase"] == "Goodbye!"
    assert out["meta"]["paused"] is False
    assert out["meta"]["closed"] is True
    assert out["meta"]["voice"] == "default"

def test_run_session_no_input_mutation(monkeypatch, fake_inputs):
    user_state, history, flow_context, raw_response = fake_inputs
    user_state_copy = copy.deepcopy(user_state)
    history_copy = copy.deepcopy(history)
    flow_context_copy = copy.deepcopy(flow_context)
    monkeypatch.setattr("reflecto.orchestrator.run_reflecto", lambda *a, **k: {
        "avatar_prompt": "A", "questions": [], "response": None, "presence": {}, "continuity_phrase": None, "closing_phrase": None, "paused": False, "closed": False, "voice": ""
    })
    run_session(user_state, history, flow_context, raw_response)
    assert user_state == user_state_copy
    assert history == history_copy
    assert flow_context == flow_context_copy

def test_run_session_missing_keys(monkeypatch, fake_inputs):
    user_state, history, flow_context, raw_response = fake_inputs
    monkeypatch.setattr("reflecto.orchestrator.run_reflecto", lambda *a, **k: {})
    out = run_session(user_state, history, flow_context, raw_response)
    assert set(out.keys()) == {"avatar_prompt", "questions", "response", "presence", "continuity_phrase", "closing_phrase", "meta"}
    assert isinstance(out["questions"], list)
    assert isinstance(out["presence"], dict)
    assert isinstance(out["meta"], dict)

def test_run_session_orchestrator_called_once(monkeypatch, fake_inputs):
    user_state, history, flow_context, raw_response = fake_inputs
    call_count = {"count": 0}
    def fake_run_reflecto(*a, **k):
        call_count["count"] += 1
        return {}
    monkeypatch.setattr("reflecto.orchestrator.run_reflecto", fake_run_reflecto)
    run_session(user_state, history, flow_context, raw_response)
    assert call_count["count"] == 1

def test_run_session_graceful_missing_raw_response(monkeypatch, fake_inputs):
    user_state, history, flow_context, _ = fake_inputs
    monkeypatch.setattr("reflecto.orchestrator.run_reflecto", lambda *a, **k: {"avatar_prompt": "A"})
    out = run_session(user_state, history, flow_context)
    assert out["avatar_prompt"] == "A"
