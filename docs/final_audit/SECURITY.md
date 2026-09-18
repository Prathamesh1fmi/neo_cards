# Security Audit

## IPC Constraints
- Rust `AppError` strips all internal filesystem paths and raw SQL query strings before serialization to prevent Webview exploitation.

## Plugin Sandbox
- Least-Privilege access. `PluginContext` blocks `DatabaseWrite` unless the user explicitly grants it. 
- Crash isolation: Plugins running in background V8/Deno environments cannot panic the main Tauri process.

## Encryption
- The SyncEngine utilizes AES-256-GCM. The Cloud/Transport layer only ever receives opaque ciphertext blobs. SQLite database remains unencrypted on the local machine (standard desktop practice), but credentials (e.g., OpenAI API Keys) are stored in the OS Keychain.