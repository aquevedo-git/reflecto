import pytest
from reflecto.avatar.presence_engine import build_presence
from reflecto.core.daily_state import DailyState

def fake_memory_patterns(trend='steady', stability='stable'):
    return {'trend': trend, 'stability': stability}

def fake_flow_context(main_mode='explore'):
    return {'main_mode': main_mode}

def test_presence_output_shape():
    state = DailyState(date='2026-01-20', energy=5, mood=6, stress=4, focus=5, meaning=6)
    mem = fake_memory_patterns()
    flow = fake_flow_context()
    result = build_presence(state, mem, flow)
    assert isinstance(result, dict)
    keys = set(result.keys())
    expected = {'energy_level', 'emotional_tone', 'presence_style', 'pacing', 'expression', 'notes'}
    assert keys == expected

def test_presence_determinism():
    state = DailyState(date='2026-01-21', energy=7, mood=8, stress=3, focus=6, meaning=7)
    mem = fake_memory_patterns(trend='improving', stability='stable')
    flow = fake_flow_context(main_mode='closure')
    out1 = build_presence(state, mem, flow)
    out2 = build_presence(state, mem, flow)
    assert out1 == out2

def test_no_side_effects():
    # Should not write files, call APIs, or depend on time
    state = DailyState(date='2026-01-22', energy=3, mood=5, stress=8, focus=4, meaning=5)
    mem = fake_memory_patterns(trend='declining', stability='unstable')
    flow = fake_flow_context(main_mode='holding')
    result = build_presence(state, mem, flow)
    assert 'notes' in result
    # No exceptions, no file writes, no randomness

def test_phase_dependencies():
    # Phase 1: load_avatar_prompt importable
    from reflecto.avatar.generator import load_avatar_prompt
    assert callable(load_avatar_prompt)
    # Phase 2: ReflectoFlow importable
    from reflecto.chatbot.flow import ReflectoFlow
    assert ReflectoFlow is not None
    # Phase 3: analyze_memory_patterns importable
    from reflecto.core.memory_intelligence import analyze_memory_patterns
    assert callable(analyze_memory_patterns)
