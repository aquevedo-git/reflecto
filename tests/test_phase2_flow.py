import pytest
from reflecto.chatbot.flow import run_reflecto_flow

def fake_answer_callback(prompt):
    return "Short answer."

def test_normal_energy_flow():
    user_state = {
        'user_id': 'test_user',
        'energy': 7
    }
    prompts = run_reflecto_flow(user_state, fake_answer_callback)
    assert isinstance(prompts, list)
    assert len(prompts) > 2  # Should ask all questions
    # No errors should occur
    assert all(isinstance(p, str) for p in prompts)

def test_low_energy_flow_gentle_close():
    user_state = {
        'user_id': 'test_user',
        'energy': 2
    }
    prompts = run_reflecto_flow(user_state, fake_answer_callback)
    assert isinstance(prompts, list)
    assert len(prompts) >= 2  # Only 2 questions + gentle close
    last_prompt = prompts[-1].lower()
    assert (
        'gentle' in last_prompt or 'rest' in last_prompt or 'take care' in last_prompt
    ), "Gentle closing message missing in last prompt"

def test_deep_reflection_offered_optional():
    user_state = {
        'user_id': 'test_user',
        'energy': 7
    }
    prompts = run_reflecto_flow(user_state, lambda p: "no" if "deep" in p.lower() else "Short answer.")
    # Should not error, and should offer deep reflection
    offered = any("deep" in p.lower() for p in prompts)
    assert offered
    # User can opt out (simulate with 'no')
    # No errors should occur
    assert all(isinstance(p, str) for p in prompts)

def test_flow_no_errors():
    user_state = {
        'user_id': 'test_user',
        'energy': 5
    }
    try:
        prompts = run_reflecto_flow(user_state, fake_answer_callback)
    except Exception as e:
        pytest.fail(f"Flow raised an exception: {e}")
    assert isinstance(prompts, list)
