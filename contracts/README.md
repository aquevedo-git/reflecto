# Reflecto Contracts

This folder defines the *only allowed* shapes of data exchanged between backend and frontend.

## SSE Event Contract (source of truth)
All SSE events must match `session_events.json`.

Backend must emit:
- heartbeat
- presence
- skills
- time_of_day

Frontend must consume these shapes only.
No other keys are guaranteed.
