# ADR 0012: Conflict Resolution
## Context
Two offline devices may edit the same Note simultaneously.
## Decision
We establish a Pluggable Conflict Resolver. The MVP uses Last Write Wins (LWW) via timestamps, but the architecture explicitly permits CRDT (Conflict-free Replicated Data Type) adoption for future document-level merging.