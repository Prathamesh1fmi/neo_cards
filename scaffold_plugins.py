import os
from pathlib import Path

base = Path('.')

dirs = [
    'src-tauri/src/application/plugins',
    'src/plugins/core',
    'plugins/example-plugin',
    'docs/sdk',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. Rust Plugin Manifest
scripts['src-tauri/src/application/plugins/manifest.rs'] = r'''use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginManifest {
    pub id: String,
    pub name: String,
    pub author: String,
    pub description: String,
    pub version: String,
    pub minimum_core_version: String,
    pub maximum_core_version: Option<String>,
    pub permissions: Vec<Permission>,
    pub entrypoint: String,
    pub icon: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum Permission {
    FileSystem,
    Media,
    DatabaseRead,
    DatabaseWrite,
    ReviewEngine,
    CommandPalette,
    Notifications,
}
'''

# 2. Rust Plugin Manager & Lifecycle
scripts['src-tauri/src/application/plugins/manager.rs'] = r'''use std::collections::HashMap;
use crate::application::plugins::manifest::PluginManifest;
use crate::error::AppError;

pub enum PluginState {
    Discovered,
    Validated,
    Loaded,
    Running,
    Crashed(String),
}

pub struct PluginContext {
    pub manifest: PluginManifest,
    pub state: PluginState,
}

pub struct PluginManager {
    plugins: HashMap<String, PluginContext>,
}

impl PluginManager {
    pub fn new() -> Self {
        Self { plugins: HashMap::new() }
    }

    pub fn discover(&mut self, plugin_dir: &std::path::Path) -> Result<(), AppError> {
        // MOCK: Reads plugin.json from directories, validates schema, checks core version compatibility.
        Ok(())
    }

    pub fn load_plugin(&mut self, plugin_id: &str) -> Result<(), AppError> {
        // MOCK: Verifies permissions, sandboxes execution environment (e.g. Deno/V8 or WASM), executes entrypoint.
        Ok(())
    }
}
'''

# 3. Rust Event Bus
scripts['src-tauri/src/application/plugins/events.rs'] = r'''use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AppEvent {
    NoteCreated { note_id: String },
    NoteUpdated { note_id: String },
    CardReviewed { card_id: String, rating: i32 },
    DeckCreated { deck_id: String },
    PluginLoaded { plugin_id: String },
}

type EventHandler = Box<dyn Fn(&AppEvent) + Send + Sync>;

pub struct EventBus {
    listeners: HashMap<String, Vec<EventHandler>>,
}

impl EventBus {
    pub fn new() -> Self {
        Self { listeners: HashMap::new() }
    }

    pub fn publish(&self, event: AppEvent) {
        // MOCK: Dispatches event to all registered plugin listeners.
    }
}
'''

# 4. React Plugin Registry (Dynamic UI Contribution)
scripts['src/plugins/core/registry.ts'] = r'''import React from 'react';

type UIContext = 'sidebar' | 'command_palette' | 'editor_toolbar' | 'inspector' | 'review_actions';

export interface PluginComponent {
    id: string;
    context: UIContext;
    component: React.FC<any>;
    priority?: number;
}

class PluginRegistry {
    private components: Map<UIContext, PluginComponent[]> = new Map();

    registerComponent(pluginId: string, context: UIContext, component: React.FC<any>, priority = 0) {
        const current = this.components.get(context) || [];
        this.components.set(context, [...current, { id: pluginId, context, component, priority }].sort((a, b) => (b.priority || 0) - (a.priority || 0)));
    }

    getComponents(context: UIContext): PluginComponent[] {
        return this.components.get(context) || [];
    }
}

export const registry = new PluginRegistry();
'''

# 5. Example Plugin Manifest
scripts['plugins/example-plugin/plugin.json'] = r'''{
  "id": "com.neocards.pomodoro",
  "name": "Pomodoro Timer",
  "author": "NeoCards Team",
  "description": "Adds a native Pomodoro timer to the Review interface.",
  "version": "1.0.0",
  "minimum_core_version": "0.1.0",
  "permissions": ["notifications", "reviewengine"],
  "entrypoint": "main.js",
  "icon": "icon.png"
}'''

# 6. Example Plugin Code
scripts['plugins/example-plugin/main.js'] = r'''// NeoCards Plugin SDK Example
import { ui, events, notifications } from '@neocards/sdk';
import React, { useState, useEffect } from 'react';

const PomodoroWidget = () => {
    const [timeLeft, setTimeLeft] = useState(25 * 60);
    
    useEffect(() => {
        const timer = setInterval(() => setTimeLeft(t => Math.max(0, t - 1)), 1000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        if (timeLeft === 0) {
            notifications.show({ title: "Pomodoro Complete!", body: "Time for a 5 minute break." });
        }
    }, [timeLeft]);

    return (
        <div style={{ padding: '8px', border: '1px solid var(--border)', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold' }}>Pomodoro</div>
            <div>{Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}</div>
        </div>
    );
};

export function activate(context) {
    console.log("Pomodoro Plugin Activated!");
    
    // Register UI Component in the Sidebar
    ui.registerComponent('sidebar', PomodoroWidget, 100);

    // Listen to backend events
    events.on('CardReviewed', (event) => {
        console.log(`Card ${event.card_id} was reviewed!`);
    });
}

export function deactivate() {
    console.log("Pomodoro Plugin Deactivated.");
}
'''

# 7. SDK Documentation
scripts['docs/sdk/index.md'] = r'''# NeoCards Plugin SDK

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
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Plugin SDK Scaffolding complete.")

