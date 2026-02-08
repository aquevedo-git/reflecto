import pytest
from reflecto.avatar.voice_engine import apply_voice

def test_minimal_voice():
    text = "You did well today. You showed up anyway."
    presence = {"emotional_tone": "neutral", "energy_level": "high"}
    silence = {"should_close": True}
    continuity = {}
    result = apply_voice(text, presence, silence, continuity)
    assert result["voice"] == "minimal"
    assert "condensed" in result["notes"]
    assert "You did well today" in result["text"]
    assert "showed up anyway" not in result["text"] or len(result["text"]) < len(text)
    assert result["text"] != text


def test_soft_voice():
    text = "You did well today. You showed up anyway."
    presence = {"emotional_tone": "warm", "energy_level": "high"}
    silence = {"should_close": False}
    continuity = {}
    result = apply_voice(text, presence, silence, continuity)
    assert result["voice"] == "soft"
    assert "gentle cadence" in result["notes"]
    assert "Take care." in result["text"]
    assert text.split('.')[0] in result["text"]
    assert result["text"] != text


def test_grounded_voice():
    text = "You did well today, you showed up anyway."
    presence = {"emotional_tone": "neutral", "energy_level": "low"}
    silence = {"should_close": False}
    continuity = {}
    result = apply_voice(text, presence, silence, continuity)
    assert result["voice"] == "grounded"
    assert "slower rhythm" in result["notes"]
    assert "," not in result["text"]
    assert result["text"].count('.') >= 2
    assert result["text"] != text


def test_steady_voice():
    text = "You did well today. You showed up anyway."
    presence = {"emotional_tone": "neutral", "energy_level": "high"}
    silence = {"should_close": False}
    continuity = {}
    result = apply_voice(text, presence, silence, continuity)
    assert result["voice"] == "steady"
    assert "neutral" in result["notes"]
    assert result["text"] == text


def test_determinism_and_no_mutation():
    text = "You did well today. You showed up anyway."
    presence = {"emotional_tone": "warm", "energy_level": "high"}
    silence = {"should_close": False}
    continuity = {}
    orig_text = text[:]
    orig_presence = dict(presence)
    orig_silence = dict(silence)
    orig_continuity = dict(continuity)
    result1 = apply_voice(text, presence, silence, continuity)
    result2 = apply_voice(text, presence, silence, continuity)
    assert result1 == result2
    assert text == orig_text
    assert presence == orig_presence
    assert silence == orig_silence
    assert continuity == orig_continuity


def test_no_content_loss():
    text = "You did well today. You showed up anyway."
    presence = {"emotional_tone": "warm", "energy_level": "high"}
    silence = {"should_close": False}
    continuity = {}
    result = apply_voice(text, presence, silence, continuity)
    for clause in ["You did well today", "You showed up anyway"]:
        assert clause.split()[0] in result["text"]


def test_minimal_voice_keeps_meaning():
    text = "You did well today. You showed up anyway."
    presence = {"emotional_tone": "neutral", "energy_level": "high"}
    silence = {"should_close": True}
    continuity = {}
    result = apply_voice(text, presence, silence, continuity)
    assert "did well" in result["text"]
    # Should not add advice or new content
    assert "advice" not in result["text"].lower()
    assert "remember" not in result["text"].lower()


def test_priority_order():
    text = "You did well today. You showed up anyway."
    presence = {"emotional_tone": "warm", "energy_level": "low"}
    silence = {"should_close": True}
    continuity = {}
    result = apply_voice(text, presence, silence, continuity)
    assert result["voice"] == "minimal"  # silence.should_close wins


def test_no_dependency_on_earlier_phases():
    text = "Some message."
    presence = {}
    silence = {}
    continuity = {}
    result = apply_voice(text, presence, silence, continuity)
    assert isinstance(result, dict)
    assert "voice" in result
    assert "text" in result
    assert "notes" in result
