import pytest
from reflecto.core.memory_intelligence import MemoryPatterns, analyze_memory_patterns

# Sample history entries for tests
def make_entry(mood, stressor, focus, theme, energy, meaning):
    return {
        'mood': mood,
        'stressor': stressor,
        'focus': focus,
        'theme': theme,
        'energy': energy,
        'meaning': meaning
    }

def test_no_patterns_with_less_than_3_days():
    history = [
        make_entry('happy', 'work', 'reading', 'growth', 7, 6),
        make_entry('sad', 'family', 'exercise', 'health', 5, 5)
    ]
    patterns = analyze_memory_patterns(history)
    assert all(len(getattr(patterns, field)) == 0 for field in [
        'recurring_moods', 'recurring_stressors', 'recurring_focus_patterns', 'recurring_themes'
    ])
    assert patterns.energy_trend == 'stable'
    assert patterns.meaning_trend == 'stable'

def test_weak_patterns_at_3_days():
    history = [
        make_entry('happy', 'work', 'reading', 'growth', 7, 6),
        make_entry('happy', 'work', 'reading', 'growth', 6, 6),
        make_entry('happy', 'work', 'reading', 'growth', 7, 7)
    ]
    patterns = analyze_memory_patterns(history)
    assert 'happy' in patterns.recurring_moods
    assert 'work' in patterns.recurring_stressors
    assert 'reading' in patterns.recurring_focus_patterns
    assert 'growth' in patterns.recurring_themes
    assert patterns.energy_trend in ['stable', 'rising', 'declining']
    assert patterns.meaning_trend in ['stable', 'rising', 'declining']

def test_strong_patterns_at_7_days():
    history = [
        make_entry('happy', 'work', 'reading', 'growth', 7, 6),
        make_entry('happy', 'work', 'reading', 'growth', 6, 6),
        make_entry('happy', 'work', 'reading', 'growth', 7, 7),
        make_entry('happy', 'work', 'reading', 'growth', 7, 7),
        make_entry('happy', 'work', 'reading', 'growth', 8, 8),
        make_entry('happy', 'work', 'reading', 'growth', 7, 7),
        make_entry('happy', 'work', 'reading', 'growth', 7, 7)
    ]
    patterns = analyze_memory_patterns(history)
    assert patterns.recurring_moods.count('happy') == 1
    assert patterns.recurring_stressors.count('work') == 1
    assert patterns.recurring_focus_patterns.count('reading') == 1
    assert patterns.recurring_themes.count('growth') == 1
    assert patterns.energy_trend in ['stable', 'rising', 'declining']
    assert patterns.meaning_trend in ['stable', 'rising', 'declining']

def test_raw_history_immutable():
    history = [
        make_entry('happy', 'work', 'reading', 'growth', 7, 6),
        make_entry('sad', 'family', 'exercise', 'health', 5, 5)
    ]
    history_copy = [entry.copy() for entry in history]
    _ = analyze_memory_patterns(history)
    assert history == history_copy

def test_memory_intelligence_deterministic():
    history = [
        make_entry('happy', 'work', 'reading', 'growth', 7, 6),
        make_entry('happy', 'work', 'reading', 'growth', 6, 6),
        make_entry('happy', 'work', 'reading', 'growth', 7, 7)
    ]
    patterns1 = analyze_memory_patterns(history)
    patterns2 = analyze_memory_patterns(history)
    assert patterns1 == patterns2
