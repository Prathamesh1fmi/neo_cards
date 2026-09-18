# NeoCards Plugin SDK

Welcome to the NeoCards Extension Platform. 
NeoCards exposes a heavily sandboxed, versioned API for building powerful desktop integrations.

## Architecture
NeoCards uses a layered plugin architecture. 
- **Backend (Rust)**: Handles capabilities like FileSystem access and Database reads. Plugins cannot execute raw SQL. They must use the `neocards::api::note` stable traits.
- **Frontend (React)**: Handles UI contributions. Plugins register React components into predefined dropzones (e.g., `sidebar`, `command_palette`, `inspector`).

## The `plugin.json` Manifest
Every plugin requires a manifest. It declares compatibility bounds (`minimum_core_version`) to prevent crashes during NeoCards updates, and explicitly lists `permissions`. 

## Permissions
Plugins operate on a principle of Least Privilege.
If your plugin attempts to use `notifications.show()` but `"notifications"` is not in your manifest, the SDK will throw an `AccessDenied` error.

Supported Permissions:
- `filesystem`
- `media`
- `databaseread`
- `databasewrite`
- `reviewengine`
- `commandpalette`
- `notifications`

## Events
The Event Bus allows plugins to react to global state changes without polling.
```javascript
events.on('NoteCreated', (e) => {
    console.log("A new note was added:", e.note_id);
});
```