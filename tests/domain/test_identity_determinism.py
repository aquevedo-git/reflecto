from domain.core.identity_crystallizer import crystallize


def test_crystallize_deterministic_with_pattern_ordering():
    identity = {}
    patterns_a = {
        "recurring_moods": ["calm", "steady"],
        "recurring_themes": ["growth"],
    }
    patterns_b = {
        "recurring_themes": ["growth"],
        "recurring_moods": ["steady", "calm"],
    }

    out1 = crystallize(identity, patterns_a, day="2026-02-08")
    out2 = crystallize(identity, patterns_b, day="2026-02-08")

    assert out1 == out2
