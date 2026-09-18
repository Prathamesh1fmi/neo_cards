# ADR 0008: Media Architecture

## Context
Storing Base64 images inside JSON documents bloats the database, degrades performance, and breaks sync algorithms.

## Decision
We will use Media Reference Objects. Binary files (Images, Audio, PDF) will be hashed (SHA-256) and saved to the local file system (`~/.neocards/media/`). The JSON document will only store a reference: `{ "type": "image", "attrs": { "hash": "abc123..." } }`.

## Consequences
- **Positive**: Notes remain kilobytes in size. SQLite stays lightning fast. Deduplication is automatic (same image pasted twice equals one file on disk).
- **Negative**: File system syncing is required alongside database syncing in the future.