"""
Streaming service for progressive delivery of session output via SSE.
"""


from persistence.session_repository import SessionRepository


from persistence.session_repository import SessionRepository

def stream_session_events(session_id: str):
    """
    Streams session events from stored session data only.
    Strictly accepts session_id, loads session, and yields events in required order.
    """
    import json
    import asyncio
    repo = SessionRepository()
    record = repo.get(session_id)
    if not record or 'data' not in record:
        yield f"event: error\ndata: {json.dumps('Session not found')}\n\n"
        return
    session = record['data']
    # Event order: avatar, questions, response_chunk(s), presence, closing, done
    if "avatar_prompt" in session:
        yield f"event: avatar\ndata: {json.dumps(session['avatar_prompt'])}\n\n"
    if "questions" in session:
        yield f"event: questions\ndata: {json.dumps(session['questions'])}\n\n"
    if "response" in session:
        resp = session["response"]
        if isinstance(resp, list):
            for chunk in resp:
                yield f"event: response_chunk\ndata: {json.dumps(chunk)}\n\n"
        else:
            yield f"event: response_chunk\ndata: {json.dumps(resp)}\n\n"
    # Initial presence event (optional, for immediate feedback)
    # yield f"event: presence\ndata: {json.dumps({'status': 'stream_opened'})}\n\n"
    # Phase 15.3: Emit static skills event for frontend animation
    if "presence" in session:
        yield f"event: skills\ndata: {json.dumps({'financial': 50, 'health': 50, 'focus': 50, 'relationships': 50})}\n\n"

    # --- Session Heartbeat Loop ---
    import random
    import logging
    import datetime
    skills = {"financial": 50, "health": 50, "focus": 50, "relationships": 50}
    def clamp(val):
        return max(0, min(100, val))
    session_active = True
    async def heartbeat_loop():
        while session_active:
            now = datetime.datetime.now()
            hour = now.hour
            # Determine time_of_day
            if 5 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 17:
                time_of_day = "afternoon"
            elif 17 <= hour < 21:
                time_of_day = "evening"
            else:
                time_of_day = "night"
            # Determine state
            if time_of_day == "night":
                state = "SLEEPING"
            elif time_of_day == "evening":
                state = "HOLDING"
            else:
                state = "AWAKE"
            presence_payload = {
                "type": "presence",
                "state": state,
                "timeOfDay": time_of_day
            }
            print("heartbeat tick")
            yield f"event: presence\ndata: {json.dumps(presence_payload)}\n\n"
            # Skills update
            for k in skills:
                skills[k] = clamp(skills[k] + random.randint(-1, 1))
            yield f"event: skills\ndata: {json.dumps(skills)}\n\n"
            await asyncio.sleep(3)

    # Run the heartbeat async generator
    async def run_async_gen(gen):
        try:
            async for event in gen:
                yield event
        except StopAsyncIteration:
            pass

    # If running in an async context, yield from the async generator
    # This is required for FastAPI SSE
    return run_async_gen(heartbeat_loop())
