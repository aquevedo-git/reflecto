import pytest
from reflecto.avatar.silence_engine import decide_silence

def test_determinism():
    presence = {"energy": 4, "stress": 5, "pacing": "steady", "tone": "neutral"}
    memory_patterns = {"meaning_trend": "steady"}
    flow_context = {"questions_asked": 3}
    out1 = decide_silence(presence, memory_patterns, flow_context)
    out2 = decide_silence(presence, memory_patterns, flow_context)
    assert out1 == out2

def test_low_energy_triggers_pause():
    presence = {"energy": 4, "stress": 5, "pacing": "steady", "tone": "neutral"}
    memory_patterns = {"meaning_trend": "steady"}
    flow_context = {"questions_asked": 2}
    result = decide_silence(presence, memory_patterns, flow_context)
    assert result["should_pause"] is True
    assert result["pause_type"] in ("short", "long")

def test_high_stress_triggers_pause():
    presence = {"energy": 7, "stress": 8, "pacing": "steady", "tone": "neutral"}
    memory_patterns = {"meaning_trend": "steady"}
    flow_context = {"questions_asked": 2}
    result = decide_silence(presence, memory_patterns, flow_context)
    assert result["should_pause"] is True

def test_declining_meaning_triggers_pause():
    presence = {"energy": 7, "stress": 5, "pacing": "steady", "tone": "neutral"}
    memory_patterns = {"meaning_trend": "declining"}
    flow_context = {"questions_asked": 2}
    result = decide_silence(presence, memory_patterns, flow_context)
    assert result["should_pause"] is True

def test_long_interaction_triggers_closure():
    presence = {"energy": 7, "stress": 5, "pacing": "steady", "tone": "neutral"}
    memory_patterns = {"meaning_trend": "steady"}
    flow_context = {"questions_asked": 7}
    result = decide_silence(presence, memory_patterns, flow_context)
    assert result["should_close"] is True
    assert result["closure_style"] in ("gentle", "warm")

def test_silence_does_not_mutate_inputs():
    presence = {"energy": 4, "stress": 5, "pacing": "steady", "tone": "neutral"}
    memory_patterns = {"meaning_trend": "steady"}
    flow_context = {"questions_asked": 3}
    presence_copy = presence.copy()
    memory_patterns_copy = memory_patterns.copy()
    flow_context_copy = flow_context.copy()
    decide_silence(presence, memory_patterns, flow_context)
    assert presence == presence_copy
    assert memory_patterns == memory_patterns_copy
    assert flow_context == flow_context_copy
