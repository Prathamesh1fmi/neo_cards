# ADR 0006: JSON Storage Strategy

## Context
Storing HTML directly in SQLite is space-efficient but structurally opaque.

## Decision
The canonical source of truth for all Note fields will be the ProseMirror / Tiptap JSON AST format. 
We will store this JSON string directly in the `notes.content` SQLite column.

## Consequences
- **Positive**: Perfectly preserves editor metadata, block types, marks, and media references. It allows unlimited undo history (since ProseMirror states are easily diffable JSON).
- **Negative**: JSON payload is slightly larger than raw HTML. FTS search requires a dedicated extraction step before saving.