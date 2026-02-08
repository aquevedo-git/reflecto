from copy import deepcopy

import hypothesis.strategies as st
from hypothesis import given, settings

from domain.core.memory_intelligence import analyze_memory_patterns
from domain.core.snapshot_builder import build_daily_snapshot, MEANINGFUL_EVENT_TYPES
from domain.core.streaks import compute_streak
from domain.core.identity_service import update_identity


@settings(max_examples=50)
@given(
    history=st.lists(
        st.fixed_dictionaries(
            {
                "energy": st.integers(min_value=1, max_value=10),
                "meaning": st.integers(min_value=1, max_value=10),
            },
            optional={
                "mood": st.one_of(st.text(min_size=0, max_size=6), st.none()),
                "stressor": st.one_of(st.text(min_size=0, max_size=6), st.none()),
                "focus": st.one_of(st.text(min_size=0, max_size=6), st.none()),
                "theme": st.one_of(st.text(min_size=0, max_size=6), st.none()),
            }
        ),
        max_size=10,
    )
)
def test_analyze_memory_patterns_deterministic_and_no_mutation(history):
    original = deepcopy(history)
    out1 = analyze_memory_patterns(history)
    out2 = analyze_memory_patterns(history)
    assert out1 == out2
    assert history == original


@settings(max_examples=50)
@given(
    events=st.lists(
        st.fixed_dictionaries(
            {
                "type": st.sampled_from(["presence", "skills", "time_of_day", "other"]),
                "payload": st.dictionaries(
                    keys=st.text(min_size=1, max_size=6),
                    values=st.integers(min_value=0, max_value=10),
                    max_size=3,
                ),
            }
        ),
        max_size=20,
    )
)
def test_build_daily_snapshot_deterministic(events):
    out1 = build_daily_snapshot(events)
    out2 = build_daily_snapshot(events)
    assert out1 == out2
    assert sum(out1["counts"].values()) == len(events)
    expected_meaningful = sum(1 for e in events if e["type"] in MEANINGFUL_EVENT_TYPES)
    assert out1["meaningful_events"] == expected_meaningful


@settings(max_examples=50)
@given(
    meaningful_events=st.lists(st.integers(min_value=0, max_value=3), min_size=0, max_size=15)
)
def test_compute_streak_properties(meaningful_events):
    snapshots = [{"snapshot": {"meaningful_events": v}} for v in meaningful_events]
    streak = compute_streak(snapshots)
    if not meaningful_events:
        assert streak == 0
    elif meaningful_events[0] == 0:
        assert streak == 0
    elif all(v > 0 for v in meaningful_events):
        assert streak == len(meaningful_events)
    else:
        # streak should stop at first zero
        first_zero = meaningful_events.index(0)
        assert streak == first_zero


@settings(max_examples=50)
@given(
    identity=st.dictionaries(keys=st.text(min_size=1, max_size=6), values=st.integers(min_value=0, max_value=5), max_size=5),
    patterns=st.dictionaries(keys=st.text(min_size=1, max_size=6), values=st.lists(st.text(min_size=0, max_size=6), max_size=3), max_size=5),
)
def test_update_identity_pure_and_deterministic(identity, patterns):
    identity_copy = deepcopy(identity)
    out1 = update_identity(identity, patterns)
    out2 = update_identity(identity, patterns)
    assert out1 == out2
    assert identity == identity_copy
