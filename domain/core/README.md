# Reflecto Core (Frozen)

This directory is **frozen after v1.0**.

Rules:
- No external imports
- No LLM calls
- No IO
- No UI
- No adapters
- No side effects
- Only pure logic

All changes require:
- New tests
- Explicit version bump
- Review

Violations break the contract.
