from reflecto.chatbot.memory import update_memory


def test_update_memory_does_not_mutate_input():
    old_memory = {"history": [{"date": "2026-02-06", "mood": 5}]}
    old_snapshot = list(old_memory["history"])

    today_state = {"date": "2026-02-07", "mood": 6}
    _ = update_memory(old_memory, today_state)

    assert old_memory["history"] == old_snapshot
