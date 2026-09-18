# ADR 0015: RAG Pipeline
## Context
LLMs cannot fit 100,000 notes into their context window.
## Decision
We implement Retrieval-Augmented Generation (RAG). Before querying the LLM, Rust queries SQLite FTS5 and the Embedding cache to find the top 5 most relevant notes. Only these specific, ranked chunks are injected into the Prompt Builder.