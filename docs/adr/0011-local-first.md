# ADR 0011: Local-First Principle
## Context
Web apps rely on the cloud as the source of truth, causing latency and offline failures.
## Decision
SQLite is the canonical source of truth. Every save operation writes to SQLite immediately and returns Success. Sync is purely a background replication task. If the server goes down for a month, the app functions 100% normally.