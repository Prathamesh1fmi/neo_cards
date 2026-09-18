# Known Limitations (v1.0 Tech Debt)

- **CRDT Resolution**: SyncEngine currently defaults to Last-Write-Wins (LWW) via timestamps. True document-level merging via CRDT (Yjs/Automerge) is deferred to v1.2.
- **Audio/Video Media**: Hashing logic works for Images, but streaming large video binaries over the SyncEngine chunking mechanism requires deeper optimization.
- **AI Streaming Cancellation**: If a user closes the AI Sidebar while the LLM is streaming, the Rust thread currently finishes generating the payload before dropping, wasting CPU cycles. Abort signals needed.