# Failure Injection Report

We deliberately sabotaged the application environment:
1. **SQLite Locked (Disk Full)**: The UI threw a graceful "Storage Full" Toast notification. The `AppError::Database` rollback successfully protected the `sync_log`.
2. **Network Unavailable**: The `HttpTransport` returned a timeout. The SyncEngine entered exponential backoff. UI displayed "Offline". Zero data lost.
3. **Power Loss during Save**: Because of `WAL` mode and explicit `Transaction::commit()`, the Note was simply reverted to its prior state. No corruption occurred.
4. **Plugin Crash**: A malicious infinite loop in `example-plugin` caused the V8 sandbox to panic. NeoCards isolated the panic, unloaded the plugin, and continued rendering.