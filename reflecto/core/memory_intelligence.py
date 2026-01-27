from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class MemoryPatterns:
    recurring_moods: List[str] = field(default_factory=list)
    recurring_stressors: List[str] = field(default_factory=list)
    recurring_focus_patterns: List[str] = field(default_factory=list)
    recurring_themes: List[str] = field(default_factory=list)
    energy_trend: str = "stable"
    meaning_trend: str = "stable"

    def __eq__(self, other):
        if not isinstance(other, MemoryPatterns):
            return False
        return (
            self.recurring_moods == other.recurring_moods and
            self.recurring_stressors == other.recurring_stressors and
            self.recurring_focus_patterns == other.recurring_focus_patterns and
            self.recurring_themes == other.recurring_themes and
            self.energy_trend == other.energy_trend and
            self.meaning_trend == other.meaning_trend
        )

def analyze_memory_patterns(history: List[dict]) -> MemoryPatterns:
    # Do not analyze if less than 3 days
    if len(history) < 3:
        return MemoryPatterns()

    def get_recurring(field, min_count):
        from collections import Counter
        values = [entry[field] for entry in history if field in entry]
        if not values:
            return []
        counter = Counter(values)
        threshold = 3 if len(history) < 5 else 5 if len(history) < 7 else 7
        return [k for k, v in counter.items() if v >= threshold]

    moods = get_recurring('mood', 3)
    stressors = get_recurring('stressor', 3)
    focus_patterns = get_recurring('focus', 3)
    themes = get_recurring('theme', 3)

    def trend(values):
        if len(values) < 2:
            return "stable"
        if all(v == values[0] for v in values):
            return "stable"
        if values[-1] > values[0]:
            return "rising"
        if values[-1] < values[0]:
            return "declining"
        return "stable"

    energy_trend = trend([entry['energy'] for entry in history if 'energy' in entry])
    meaning_trend = trend([entry['meaning'] for entry in history if 'meaning' in entry])

    return MemoryPatterns(
        recurring_moods=moods,
        recurring_stressors=stressors,
        recurring_focus_patterns=focus_patterns,
        recurring_themes=themes,
        energy_trend=energy_trend,
        meaning_trend=meaning_trend
    )
