![CI](https://github.com/aquevedo-git/reflecto/actions/workflows/ci.yml/badge.svg)

# Reflecto

Reflecto is a deterministic, phase-driven reflective intelligence system.

## Structure
- reflecto/       → core engine (pure, tested)
- extensions/     → optional adapters (LLMs, APIs)
- app/            → runnable entrypoints
- tests/          → phase-based specs

## Guarantees
- Core is deterministic
- Tests define behavior
- LLMs are adapters only
- No hidden logic

## Status
v1.0 core locked
