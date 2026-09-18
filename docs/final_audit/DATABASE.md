# Database Architecture

## SQLite Configuration
- `PRAGMA journal_mode = WAL`: Allows concurrent reads while writing (e.g. background Sync while the user is studying).
- `PRAGMA foreign_keys = ON`: Prevents orphaned cards when a deck is deleted.

## Key Tables
- `decks`: Self-referencing hierarchical structure (`parent_id`).
- `notes`: Contains the canonical Tiptap JSON AST payload.
- `cards`: 1-to-Many mapping from `notes`, containing `due_date`, `interval`, `ease`.
- `revlog`: Immutable ledger of every study interaction for FSRS tracking.
- `notes_fts`: Virtual FTS5 table extracting pure text from JSON for instant search.
- `sync_log`: The durable mutation queue storing operation deltas.

## Migration Safety
Migrations are run linearly via embedded SQL strings ensuring the schema is upgraded safely on user machines without data loss.