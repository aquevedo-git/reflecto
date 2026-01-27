import pytest
from reflecto.avatar.continuity_engine import decide_continuity
import copy

def test_no_recall_when_silence_closes():
    memory_patterns = {"meaning_trend": "rising"}
    silence = {"should_close": True}
    presence = {}
    flow_context = {}
    result = decide_continuity(memory_patterns, presence, silence, flow_context)
    assert result["should_recall"] is False
    assert result["recall_style"] == "none"
    assert result["recall_phrase"] is None
    assert "Silence requested closure" in result["notes"]

def test_gentle_recall_on_meaning_rising():
    memory_patterns = {"meaning_trend": "rising"}
    silence = {"should_close": False}
    presence = {}
    flow_context = {}
    result = decide_continuity(memory_patterns, presence, silence, flow_context)
    assert result["should_recall"] is True
    assert result["recall_style"] == "gentle"
    assert "gentle sense of meaning" in result["recall_phrase"]

def test_soft_reassurance_on_energy_decline():
    memory_patterns = {"energy_trend": "declining"}
    silence = {"should_close": False}
    presence = {}
    flow_context = {}
    result = decide_continuity(memory_patterns, presence, silence, flow_context)
    assert result["should_recall"] is True
    assert result["recall_style"] == "soft"
    assert "heavier lately" in result["recall_phrase"]

def test_gentle_recall_on_recurring_theme():
    memory_patterns = {"recurring_theme": "self-doubt"}
    silence = {"should_close": False}
    presence = {}
    flow_context = {}
    result = decide_continuity(memory_patterns, presence, silence, flow_context)
    assert result["should_recall"] is True
    assert result["recall_style"] == "gentle"
    assert "been visiting you lately" in result["recall_phrase"]

def test_no_recall_when_no_pattern():
    memory_patterns = {}
    silence = {"should_close": False}
    presence = {}
    flow_context = {}
    result = decide_continuity(memory_patterns, presence, silence, flow_context)
    assert result["should_recall"] is False
    assert result["recall_style"] == "none"
    assert result["recall_phrase"] is None

def test_determinism():
    memory_patterns = {"meaning_trend": "rising"}
    silence = {"should_close": False}
    presence = {}
    flow_context = {}
    result1 = decide_continuity(memory_patterns, presence, silence, flow_context)
    result2 = decide_continuity(memory_patterns, presence, silence, flow_context)
    assert result1 == result2

def test_no_mutation_of_memory():
    memory_patterns = {"meaning_trend": "rising"}
    silence = {"should_close": False}
    presence = {}
    flow_context = {}
    memory_patterns_copy = copy.deepcopy(memory_patterns)
    decide_continuity(memory_patterns, presence, silence, flow_context)
    assert memory_patterns == memory_patterns_copy
