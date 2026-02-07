# Reflecto Architecture Map

------------------------------------------
SYSTEM TYPE
------------------------------------------

Reflecto is a deterministic AI Life-OS platform composed of:

• Session orchestration engines
• Persistence replay layer
• Streaming event delivery system
• Avatar behavioral simulation
• Frontend passive event viewer


------------------------------------------
HIGH LEVEL DATA FLOW
------------------------------------------

USER INPUT
    ↓
API ROUTES
    ↓
SESSION SERVICE
    ↓
SESSION RUNNER
    ↓
ORCHESTRATOR
    ↓
AVATAR ENGINES
    ↓
PERSISTENCE
    ↓
STREAMING SERVICE
    ↓
FRONTEND SSE VIEWER


------------------------------------------
CORE MODULE LAYERS
------------------------------------------

LAYER 1 — API ENTRY
--------------------

api/main.py
api/routes/

Responsibilities:
• HTTP interface
• Route validation
• Payload conversion


------------------------------------------

LAYER 2 — SESSION CONTROL
--------------------------

session_service.py
session_runner.py

Responsibilities:
• Session creation
• Session replay
• Input packaging
• Core execution trigger


------------------------------------------

LAYER 3 — ORCHESTRATION CORE
-----------------------------

reflecto/orchestrator.py

Responsibilities:
• Runs full Reflecto logic pipeline
• Calls avatar intelligence engines
• Combines outputs into session result


------------------------------------------

LAYER 4 — AVATAR INTELLIGENCE ENGINES
-------------------------------------

presence_engine
response_shaper
continuity_engine
silence_engine
closing_engine
voice_engine
questions_engine

Responsibilities:
• Behavioral logic
• Emotional modeling
• Coaching intelligence
• Personality shaping


------------------------------------------

LAYER 5 — PERSISTENCE LAYER
----------------------------

persistence/session_repository.py
sessions.db

Responsibilities:
• Stores session outputs
• Enables deterministic replay
• Provides historical memory


------------------------------------------

LAYER 6 — STREAMING DELIVERY
----------------------------

services/streaming_service.py
api/routes/streaming.py

Responsibilities:
• SSE event generation
• Ordered event delivery
• Replay-safe streaming


------------------------------------------

LAYER 7 — FRONTEND VIEWER
--------------------------

frontend/index.html
frontend/app.js

Responsibilities:
• Passive SSE consumer
• Event rendering
• Avatar animation
• UI state visualization


------------------------------------------
STREAMING CONTRACT
------------------------------------------

Required Event Order:

1. avatar
2. questions
3. response_chunk
4. presence
5. closing
6. done


------------------------------------------
DETERMINISM GUARANTEE
------------------------------------------

Rules:

• Streaming MUST equal replay output
• Sessions MUST be reproducible
• Persistence is source of truth
• Frontend never computes logic


------------------------------------------
FUTURE ARCHITECTURE EXPANSIONS
------------------------------------------

Phase E — Live Presence Engine
Phase F — Identity Evolution
Phase G — Autonomous Avatar Behavior
Phase H — Multi-Session Timeline
Phase I — Multi-User Social Graph
