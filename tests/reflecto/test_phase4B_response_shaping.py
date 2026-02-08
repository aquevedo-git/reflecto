import pytest
from reflecto.avatar.response_shaper import shape_response

def sample_presence(energy, tone, pacing, style):
    return {
        'emotional_tone': tone,
        'energy_level': energy,
        'pacing': pacing,
        'presence_style': style,
        'expression': 'default',
    }

RAW = "It sounds like today has been heavy. You showed up anyway."

@pytest.mark.parametrize("presence,expected", [
    (sample_presence('low', 'neutral', 'normal', 'open'),
     "It sounds like today has been heavy.\n\nYou showed up anyway."),
    (sample_presence('high', 'neutral', 'normal', 'open'),
     "It sounds like today has been heavy — You showed up anyway."),
    (sample_presence('medium', 'warm', 'normal', 'open'),
     "It sounds like today has been heavy. You — and that matters showed up anyway."),
    (sample_presence('medium', 'neutral', 'slow', 'open'),
     "It sounds like today has been heavy.\nYou showed up anyway."),
    (sample_presence('medium', 'neutral', 'normal', 'contained'),
     "It sounds like today has been heavy.\nYou showed up anyway."),
])
def test_shape_response_deterministic(presence, expected):
    out1 = shape_response(RAW, presence)
    out2 = shape_response(RAW, presence)
    assert out1 == out2
    assert out1 == expected
    # Semantic preservation: all original sentences must be present (ignoring punctuation/spacing)
    import re
    def normalize(text):
        return re.sub(r'[^\w\s]', '', text).lower()
    for part in RAW.split('. '):
        if part.strip():
            # Check that all key words from the clause are present in the output (in any order)
            words = [w for w in re.findall(r'\w+', part.lower()) if len(w) > 2]
            norm_out = normalize(out1)
            for w in words:
                assert w in norm_out, f"Missing key word '{w}' from clause: {part}"
    # No hallucination, no advice, no removal
    assert 'advice' not in out1.lower()
    assert 'should' not in out1.lower()
    assert 'must' not in out1.lower()
    assert 'remember' not in out1.lower()

def test_shape_response_reversible():
    presence = sample_presence('low', 'neutral', 'normal', 'open')
    shaped = shape_response(RAW, presence)
    # Reversibility: shaping again with same presence yields same output
    assert shape_response(shaped, presence) == shaped

def test_shape_response_content_unchanged():
    presence = sample_presence('medium', 'neutral', 'normal', 'open')
    shaped = shape_response(RAW, presence)
    # All original sentences present
    for part in RAW.split('. '):
        if part.strip():
            assert part.split('.')[0] in shaped
