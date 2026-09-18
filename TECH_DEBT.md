# Technical Debt & Known Limitations

## Parsers
- `ApkgImporter`: Currently mocked. Anki's `.apkg` is an uncompressed ZIP containing an SQLite db. We must integrate `zip` crate to extract `collection.anki2` into temp, query the schema, and map Anki's `col` string fields to our `NoteType` definitions.
- `JsonImporter`: Streaming parser needed (`serde_json::Deserializer::from_reader`) to prevent OOM when importing >500MB JSON exports.

## SQLite
- `notes_fts`: The background text extraction is currently synchronous within the `save_note` transaction. If the JSON AST is massive, this blocks the main thread. Should be moved to an async `tokio` worker queue.

## Renderer
- Markdown & Math implementations in Rust are stubbed. We must integrate `pulldown-cmark` and KaTeX rendering.

## Media
- Duplicate hash detection skips copying, but we lack a background garbage collection job to delete hashes that are no longer referenced by any JSON document (orphaned media).

## UI
- The `@tanstack/react-virtual` grid in the Browser needs its sorting logic formally bound to the backend IPC to offload thousands of rows of sorting to SQLite instead of JS memory.