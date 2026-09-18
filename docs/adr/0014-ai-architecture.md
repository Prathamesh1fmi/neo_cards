# ADR 0014: AI Architecture & Privacy
## Context
Users want intelligent features (card generation, summarization) but demand strict privacy for their notes.
## Decision
AI processing is completely decoupled from React. Rust acts as the orchestrator. We support three modes: Cloud (OpenAI/Anthropic), Local (Ollama/LM Studio), and Offline-Only (Disabled). The user explicitly selects their provider. NeoCards is purely a client.