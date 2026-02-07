# Reflecto Module Map

This document provides a **structural and responsibility overview** of every major module in Reflecto.

It serves as:

• Developer navigation guide
• Architecture onboarding reference
• AI context injection file
• Dependency understanding tool
• Expansion planning map

---

# 🧭 System Overview

Reflecto is structured as a **layered cognitive platform**.

```
API → Application (emerging) → Domain → Engines → Persistence → Streaming → Frontend
```

Each layer has strict responsibility boundaries.

---

# 📂 Top-Level Module Responsibilities

---

## 1️⃣ api/

### Purpose

External interface layer.

Handles:

• HTTP contracts
• SSE streaming endpoints
• Input validation
• Routing orchestration

---

### Key Submodules

#### api/main.py

Application entry point.

Responsibilities:

• FastAPI initialization
• Router registration
• Middleware setup
• Lifecycle event handling

---

#### api/routes/

##### streaming.py

SSE session streaming endpoint.

Responsibilities:

• Accept session payload
• Trigger session creation
• Invoke streaming service
• Return deterministic SSE stream

---

##### write.py

Handles user action ingestion.

Responsibilities:

• Accept user write events
• Persist user cognitive actions
• Feed event pipelines

---

##### daily.py

Handles daily state interactions.

Responsibilities:

• Daily state updates
• Reflection triggers
• Daily cognition hooks

---

#### api/services/

##### action_store.py

Stores user action events.

---

##### presence_engine.py

API-side presence event coordination.

(Separate from avatar engine presence modeling.)

---

#### api/contracts/

Defines external event schemas.

Includes:

• events.py
• presence.py
• write.py
• validation rules

---

---

## 2️⃣ reflecto/

### Purpose

Core cognition and intelligence domain.

This is the **Reflecto brain**.

---

### 2.1 Avatar Engines (reflecto/avatar/)

Handles avatar cognition behavior.

---

#### presence_engine.py

Models avatar awareness state.

Produces:

• Presence events
• State transitions
• Contextual awareness signals

---

#### continuity_engine.py

Maintains session narrative continuity.

---

#### response_shaper.py

Transforms raw LLM output into Reflecto personality tone.

---

#### silence_engine.py

Handles intentional silence or delayed responses.

---

#### closing_engine.py

Generates session closing reflections.

---

#### evolution.py

Handles avatar personality progression.

---

#### voice_engine.py

Controls voice / speech representation logic.

---

#### generator.py

Avatar output generation coordinator.

---

#### state.py

Avatar internal state model.

---

#### storage.py

Avatar memory persistence utilities.

---

---

### 2.2 Identity System (reflecto/core/)

Handles long-term identity crystallization.

---

#### identity_service.py

Primary identity orchestration layer.

---

#### identity_update.py

Applies identity mutation rules.

---

#### identity_crystallizer.py

Transforms short-term patterns into long-term identity traits.

---

#### identity_outputs.py

Produces identity-derived outputs.

---

#### identity_schema.py

Defines identity data structures.

---

---

### 2.3 Memory & Cognition

#### memory_intelligence.py

Extracts insights from user memory.

---

#### reflection_service.py

Generates reflection prompts and analysis.

---

#### snapshot_builder.py

Creates cognitive session snapshots.

---

#### snapshot_service.py

Manages snapshot lifecycle.

---

#### pattern_engine.py

Detects recurring behavioral patterns.

---

#### streaks.py

Tracks longitudinal behavioral streaks.

---

#### daily_state.py

Defines daily user state representation.

---

#### daily_update.py

Applies daily state transformation rules.

---

---

### 2.4 Session Runtime

#### orchestrator.py

Top-level domain orchestration engine.

Coordinates:

• Engines
• Memory
• Identity
• Response pipelines

---

#### session_runner.py

Executes full cognitive session workflow.

---

---

## 3️⃣ persistence/

### Purpose

System memory layer.

Handles durable storage.

---

#### session_repository.py

Stores and retrieves session data.

---

#### models.py

Defines persistence data structures.

---

---

## 4️⃣ services/

### Purpose

Infrastructure-level supporting services.

---

#### streaming_service.py

Deterministic session replay and SSE stream generator.

Guarantees:

• Event order stability
• Replay equivalence
• Contract formatting

---

---

## 5️⃣ frontend/

### Purpose

Presentation viewer layer.

Responsibilities:

• SSE event consumption
• Progressive rendering
• Avatar visualization
• Session playback display

Important Rule:

Frontend NEVER performs business logic.

---

---

## 6️⃣ extensions/

### Purpose

External AI provider abstraction.

---

#### llm_bridge/

Provides pluggable LLM adapters.

Includes:

• base adapter interface
• OpenAI adapter
• Mock adapter
• Future multi-provider support

---

---

## 7️⃣ contracts/

Contains JSON contract definitions.

Defines:

• Session event schema
• Event ordering guarantees

This folder represents system truth contracts.

---

---

## 8️⃣ doc/

Architecture memory layer.

Includes:

• architecture_map.md
• project_state.md
• current_phase.md
• module_map.md (this file)

---

---

## 9️⃣ tests/

Validation layer.

Covers:

• Engine correctness
• Session orchestration
• Persistence integrity
• Streaming determinism
• Contract compliance

---

# 🔄 Primary Runtime Flow

```
Client Request
    ↓
API Layer
    ↓
Session Service
    ↓
Orchestrator
    ↓
Engines + Identity + Memory
    ↓
Session Persistence
    ↓
Streaming Service
    ↓
Frontend SSE Rendering
```

---

# 🧠 Architectural Guardrails

Reflecto enforces:

• Deterministic replay
• Engine modularity
• Contract-first events
• Streaming-first UX
• Identity pipeline integrity

---

# 🚧 Planned Expansion Zones

Future modules expected:

• Application orchestration layer
• Engine Registry
• Event Bus
• Observability subsystem
• Multi-tenant user scaling
• Distributed streaming infrastructure

---

# 📌 Maintenance Rules

When adding modules:

1. Update module_map.md
2. Document responsibilities clearly
3. Maintain single-responsibility design
4. Avoid cross-layer leakage
5. Maintain replay determinism

---

# 🧭 Module Ownership Summary

| Layer       | Primary Role             |
| ----------- | ------------------------ |
| api         | External interface       |
| reflecto    | Cognitive intelligence   |
| persistence | Memory storage           |
| services    | Infrastructure utilities |
| frontend    | Visualization layer      |
| extensions  | LLM abstraction          |
| contracts   | System truth schema      |
| tests       | Validation safety net    |

---

# 🔭 Long-Term Vision

Reflecto aims to become:

• Personal cognition operating system
• Distributed AI event platform
• Identity evolution engine
• Production AI infrastructure portfolio

---

End of Module Map.
