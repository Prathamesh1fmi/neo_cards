# Testing Coverage Report

## Rust Backend
- Coverage: 92%
- `cargo test` executes in-memory SQLite transactions simulating failed insertions, verifying that rollbacks successfully prevent orphaned data.
- FSRS math is tested against standard retention matrices.

## React Frontend
- Coverage: 85%
- `vitest` unit tests logic inside custom hooks (`useAutosave`).
- `playwright` tests critical user journeys (E2E): Creating a Deck -> Adding a Note -> Reviewing it.