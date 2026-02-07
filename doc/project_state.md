# Reflecto Life-OS — Project State Snapshot

----------------------------------
Project Vision
Reflecto is a deterministic, stateful AI life companion system combining behavioral simulation, journaling, coaching, and personal analytics.

----------------------------------
Architecture Overview

WRITE → session_runner → persistence → streaming_service → frontend viewer

----------------------------------
Core Modules

session_service
session_runner
orchestrator
presence_engine
streaming_service
persistence layer
frontend SSE viewer

----------------------------------
Streaming Contract

Event Order:
1. avatar
2. questions
3. response_chunk
4. presence
5. closing
6. done

----------------------------------
Persistence

SQLite database (sessions.db)
Replay integrity required
Deterministic output guarantee

----------------------------------
Testing Status
76 automated tests passing

----------------------------------
Development Philosophy
• Deterministic output
• Replay-safe architecture
• Modular engines
• Streaming-first design
• Passive frontend

----------------------------------
Completed Phases
Phase A – Core Orchestrator
Phase B – Persistence + Replay
Phase C – Session Runner
Phase D – Deterministic Streaming

----------------------------------
Upcoming Phases
Phase E – Live Presence Core
Phase F – Identity / Memory Growth
Phase G – Avatar Behavioral Intelligence
