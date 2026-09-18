# ADR 0005: Document Engine

## Context
Our previous architecture treated HTML as the canonical data format for Notes. This is standard for web apps, but for a premium desktop application (like Obsidian or Notion), HTML destroys semantic meaning, makes Markdown/LaTeX parsing brittle, and breaks when migrating to mobile apps (React Native).

## Decision
We will build a dedicated Document Engine in Rust. The frontend (Tiptap) will act purely as an input mechanism. The Document Engine owns the Document Model (Blocks, Marks, Media References), Validation, Serialization, and the Rendering Orchestration.

## Consequences
- **Positive**: We have a strictly typed, semantic understanding of every note. We can easily extract text for FTS search, render native components on mobile, and write reliable plugins.
- **Negative**: Increased complexity. We must parse JSON ASTs in Rust and build a recursive rendering pipeline.