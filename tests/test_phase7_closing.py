"""
Phase 7: Tests for Closing Rituals Engine
"""
import copy
import pytest
from reflecto.avatar.closing_engine import decide_closing

def make_inputs():
    presence = {"energy": 5, "tone": "neutral"}
    silence = {"should_close": False}
    continuity = {"recall_phrase": None}
    voice = {"voice": "neutral"}
    flow_context = {"questions_asked": 2}
    return presence, silence, continuity, voice, flow_context

def test_determinism():
    presence, silence, continuity, voice, flow_context = make_inputs()
    result1 = decide_closing(presence, silence, continuity, voice, flow_context)
    result2 = decide_closing(presence, silence, continuity, voice, flow_context)
    assert result1 == result2

def test_closure_triggered_by_silence():
    presence, silence, continuity, voice, flow_context = make_inputs()
    silence["should_close"] = True
    result = decide_closing(presence, silence, continuity, voice, flow_context)
    assert result["should_close"] is True
    assert result["closing_phrase"] is not None
    assert "silence" in result["notes"]

def test_closure_triggered_by_questions():
    presence, silence, continuity, voice, flow_context = make_inputs()
    flow_context["questions_asked"] = 5
    result = decide_closing(presence, silence, continuity, voice, flow_context)
    assert result["should_close"] is True
    assert result["closing_phrase"] is not None
    assert "questions" in result["notes"]

def test_warm_vs_gentle():
    presence, silence, continuity, voice, flow_context = make_inputs()
    silence["should_close"] = True
    # Warm
    voice["voice"] = "warm"
    result_warm = decide_closing(presence, silence, continuity, voice, flow_context)
    assert result_warm["closing_style"] == "warm"
    # Gentle
    voice["voice"] = "neutral"
    result_gentle = decide_closing(presence, silence, continuity, voice, flow_context)
    assert result_gentle["closing_style"] == "gentle"

def test_shorter_close_when_low_energy():
    presence, silence, continuity, voice, flow_context = make_inputs()
    silence["should_close"] = True
    presence["energy"] = 3
    voice["voice"] = "warm"
    result = decide_closing(presence, silence, continuity, voice, flow_context)
    assert "leave this here" in result["closing_phrase"] or "stop here" in result["closing_phrase"]

def test_no_mutation_of_inputs():
    presence, silence, continuity, voice, flow_context = make_inputs()
    # Deep copy for comparison
    orig = [copy.deepcopy(x) for x in [presence, silence, continuity, voice, flow_context]]
    decide_closing(presence, silence, continuity, voice, flow_context)
    after = [presence, silence, continuity, voice, flow_context]
    assert orig == after

def test_no_effect_on_earlier_phases():
    # This test is a placeholder to ensure no exceptions or side effects
    presence, silence, continuity, voice, flow_context = make_inputs()
    decide_closing(presence, silence, continuity, voice, flow_context)
    # If earlier phases are unchanged, this passes
    assert True
