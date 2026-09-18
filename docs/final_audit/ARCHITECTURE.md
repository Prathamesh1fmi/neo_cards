# NeoCards Architecture Overview

NeoCards is a local-first, offline-capable learning platform.

## Core Layers
1. **Frontend (React)**: Purely a visualization and user-input layer. Uses Tailwind, shadcn/ui, and Framer Motion. Maintains zero business logic.
2. **IPC Boundary (Tauri)**: Strict typings. Commands only return Data Transfer Objects (DTOs) or `AppError`. Never raw SQL or panics.
3. **Application Services (Rust)**:
   - `SyncEngine`: Background CRDT/LWW replication.
   - `ReviewEngine`: Orchestrates FSRS queue logic.
   - `StatisticsEngine`: Aggregates historical learning data.
   - `AiOrchestrator`: RAG pipeline and Token Streaming.
   - `PluginManager`: Heavily sandboxed third-party extension loader.
4. **Domain**: Strict structs representing `Note`, `Card`, `Deck`, `DocumentNode` (Tiptap AST).
5. **Infrastructure**: `rusqlite` repositories, `Ollama` providers, and `csv` parsers.
6. **Data Store**: SQLite database running in `WAL` mode with enforced `FOREIGN_KEYS`.

## Design Principles Followed
- SOLID
- Domain Driven Design
- Clean Architecture
- Offline-First