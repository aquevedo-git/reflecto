def validate_event(event_type: str, data: dict):
    if event_type == "heartbeat":
        return "ts" in data

    if event_type == "presence":
        return "state" in data and "time_of_day" in data

    if event_type == "skills":
        return all(k in data for k in ["financial", "health", "focus", "relationships"])

    return True
