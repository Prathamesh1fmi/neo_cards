# ADR 0013: Encryption Layer
## Context
Users demand privacy for their personal knowledge bases.
## Decision
E2E encryption is decoupled from the Transport layer. The `SyncEngine` passes JSON payloads through an `Encryptor` trait before hitting the `SyncTransport`, ensuring the server only ever receives opaque ciphertext blobs.