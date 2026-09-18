import os
from pathlib import Path

base = Path('.')

dirs = [
    'docs/adr',
    'src-tauri/src/application/sync',
    'src-tauri/src/domain/sync',
    'src-tauri/src/infrastructure/sync',
    'src-tauri/src/infrastructure/network',
    'src-tauri/src/commands/sync',
    'src/features/sync/components',
    'src/features/sync/api',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. Architecture Decision Records
scripts['docs/adr/0010-sync.md'] = '''# ADR 0010: Sync Architecture
## Context
NeoCards requires multi-device synchronization without blocking the UI or demanding constant connectivity.
## Decision
We implement a background `SyncEngine` that replicates deltas from a local SQLite `sync_log` (Journal). The engine is strictly transport-agnostic, enabling users to self-host or use a future official cloud.
'''

scripts['docs/adr/0011-local-first.md'] = '''# ADR 0011: Local-First Principle
## Context
Web apps rely on the cloud as the source of truth, causing latency and offline failures.
## Decision
SQLite is the canonical source of truth. Every save operation writes to SQLite immediately and returns Success. Sync is purely a background replication task. If the server goes down for a month, the app functions 100% normally.
'''

scripts['docs/adr/0012-conflict-resolution.md'] = '''# ADR 0012: Conflict Resolution
## Context
Two offline devices may edit the same Note simultaneously.
## Decision
We establish a Pluggable Conflict Resolver. The MVP uses Last Write Wins (LWW) via timestamps, but the architecture explicitly permits CRDT (Conflict-free Replicated Data Type) adoption for future document-level merging.
'''

scripts['docs/adr/0013-encryption.md'] = '''# ADR 0013: Encryption Layer
## Context
Users demand privacy for their personal knowledge bases.
## Decision
E2E encryption is decoupled from the Transport layer. The `SyncEngine` passes JSON payloads through an `Encryptor` trait before hitting the `SyncTransport`, ensuring the server only ever receives opaque ciphertext blobs.
'''

# 2. Rust Sync Domain & Application Architecture
scripts['src-tauri/src/application/sync/mod.rs'] = r'''pub mod sync_engine;
pub mod scheduler;
pub mod replication;
pub mod delta;
pub mod journal;
pub mod snapshot;
pub mod transport;
pub mod conflict;
pub mod encryption;
pub mod compression;
pub mod protocol;
'''

scripts['src-tauri/src/application/sync/journal.rs'] = r'''use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SyncOperation {
    Insert,
    Update,
    Delete,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JournalRecord {
    pub id: String,
    pub entity: String, // "Note", "Card", "Deck"
    pub entity_id: String,
    pub operation: SyncOperation,
    pub payload_hash: String,
    pub device_id: String,
    pub timestamp: i64,
    pub synced: bool,
}

/// The durable queue tracking all local mutations.
/// Transactions write to their tables AND this journal atomically.
pub trait SyncJournal {
    fn append(&self, record: &JournalRecord) -> Result<(), String>;
    fn get_unsynced(&self) -> Result<Vec<JournalRecord>, String>;
    fn mark_synced(&self, ids: &[String]) -> Result<(), String>;
}
'''

scripts['src-tauri/src/application/sync/transport.rs'] = r'''pub trait SyncTransport {
    /// Pushes encrypted/compressed deltas to a remote server
    fn push_deltas(&self, payload: &[u8]) -> Result<(), String>;
    
    /// Pulls new remote deltas since the last sync cursor
    fn pull_deltas(&self, cursor: &str) -> Result<Vec<u8>, String>;
}

/// Example HTTP Implementation (Mocked for scaffolding)
pub struct HttpTransport {
    pub endpoint: String,
}

impl SyncTransport for HttpTransport {
    fn push_deltas(&self, _payload: &[u8]) -> Result<(), String> {
        // MOCK HTTP POST
        Ok(())
    }
    fn pull_deltas(&self, _cursor: &str) -> Result<Vec<u8>, String> {
        // MOCK HTTP GET
        Ok(vec![])
    }
}
'''

scripts['src-tauri/src/application/sync/sync_engine.rs'] = r'''use crate::application::sync::journal::SyncJournal;
use crate::application::sync::transport::SyncTransport;

pub struct SyncEngine {
    pub journal: Box<dyn SyncJournal + Send + Sync>,
    pub transport: Box<dyn SyncTransport + Send + Sync>,
    // encryptor: Box<dyn Encryptor>,
    // compressor: Box<dyn Compressor>,
}

impl SyncEngine {
    pub fn new(journal: Box<dyn SyncJournal + Send + Sync>, transport: Box<dyn SyncTransport + Send + Sync>) -> Self {
        Self { journal, transport }
    }

    /// Orchestrates the entire Push/Pull lifecycle in the background.
    pub fn execute_sync_cycle(&self) -> Result<(), String> {
        // 1. Check local unsynced records
        let pending = self.journal.get_unsynced()?;
        
        // 2. Compress & Encrypt (Skipped in mock)
        let payload = vec![]; // Serialized `pending`

        // 3. Push to Remote
        self.transport.push_deltas(&payload)?;

        // 4. Mark synced locally
        // self.journal.mark_synced(...);

        // 5. Pull from Remote
        let remote_payload = self.transport.pull_deltas("cursor123")?;
        
        // 6. Decrypt, Decompress, Resolve Conflicts, Apply to SQLite
        // ...

        Ok(())
    }
}
'''

# 3. Rust IPC Commands
scripts['src-tauri/src/commands/sync/mod.rs'] = r'''pub mod sync_commands;'''

scripts['src-tauri/src/commands/sync/sync_commands.rs'] = r'''use tauri::{State, Window};
use crate::db::connection::DbState;
use serde::Serialize;

#[derive(Serialize)]
pub struct SyncStatusDto {
    pub status: String,
    pub pending_changes: usize,
    pub last_sync: Option<String>,
}

#[tauri::command]
pub async fn trigger_manual_sync(window: Window, state: State<'_, DbState>) -> Result<(), String> {
    // Emit progress event
    let _ = window.emit("sync_event", "SyncStarted");
    let _ = window.emit("sync_event", "Uploading");
    
    // MOCK background delay
    // std::thread::sleep(std::time::Duration::from_millis(500));
    
    let _ = window.emit("sync_event", "Completed");
    Ok(())
}

#[tauri::command]
pub fn get_sync_status(state: State<DbState>) -> Result<SyncStatusDto, String> {
    Ok(SyncStatusDto {
        status: "idle".to_string(),
        pending_changes: 14,
        last_sync: Some("2 mins ago".to_string()),
    })
}
'''

# 4. React Sync Dashboard
scripts['src/features/sync/components/SyncDashboard.tsx'] = r'''import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import { Cloud, CloudOff, CloudUpload, CloudDownload, RefreshCw, Server, Shield, Database } from 'lucide-react';

export function SyncDashboard() {
  const [status, setStatus] = useState("idle");
  const [pending, setPending] = useState(0);
  const [lastSync, setLastSync] = useState("Never");

  useEffect(() => {
    // Initial load
    invoke('get_sync_status').then((res: any) => {
      setPending(res.pending_changes);
      if (res.last_sync) setLastSync(res.last_sync);
    });

    // Listen to background sync events emitted by Rust
    const unlisten = listen('sync_event', (event) => {
      setStatus(event.payload as string);
      if (event.payload === 'Completed') {
        setPending(0);
        setLastSync('Just now');
        setTimeout(() => setStatus('idle'), 2000);
      }
    });

    return () => { unlisten.then(f => f()); };
  }, []);

  const handleManualSync = async () => {
    if (status !== 'idle' && status !== 'Completed') return;
    try {
      await invoke('trigger_manual_sync');
    } catch (e) {
      console.error("Sync failed:", e);
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-background pt-8 pb-12 px-6 sm:px-12 max-w-4xl mx-auto overflow-y-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Synchronization</h1>
          <p className="text-sm text-muted-foreground mt-1">Manage local replication and cloud connections.</p>
        </div>
        <button 
          onClick={handleManualSync}
          disabled={status !== 'idle' && status !== 'Completed'}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
        >
          <RefreshCw size={14} className={status !== 'idle' && status !== 'Completed' ? 'animate-spin' : ''} />
          {status === 'idle' || status === 'Completed' ? 'Sync Now' : status}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
          <div className="text-muted-foreground mb-3 text-sm font-medium flex items-center gap-2"><Cloud size={16}/> Status</div>
          <div className="text-2xl font-semibold">{status === 'idle' ? 'Connected' : status}</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
          <div className="text-muted-foreground mb-3 text-sm font-medium flex items-center gap-2"><Database size={16}/> Unsynced Changes</div>
          <div className="text-2xl font-semibold">{pending}</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
          <div className="text-muted-foreground mb-3 text-sm font-medium flex items-center gap-2"><RefreshCw size={16}/> Last Sync</div>
          <div className="text-2xl font-semibold">{lastSync}</div>
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden mb-8">
        <div className="px-6 py-4 border-b border-border font-medium">Provider Configuration</div>
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase flex items-center gap-2 mb-2"><Server size={14}/> Transport Node</label>
              <input type="text" value="https://sync.neocards.io/v1" disabled className="w-full bg-muted/50 border border-border text-sm rounded-md px-3 py-2 cursor-not-allowed opacity-70" />
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase flex items-center gap-2 mb-2"><Shield size={14}/> E2E Encryption</label>
              <div className="flex items-center gap-2 bg-green-500/10 text-green-600 border border-green-500/20 px-3 py-2 rounded-md text-sm font-medium">
                <Shield size={16} /> Enabled (AES-256-GCM)
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-border font-medium">Change Journal Activity</div>
        <div className="p-0">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted/30 text-muted-foreground">
              <tr>
                <th className="px-6 py-3 font-medium">Entity</th>
                <th className="px-6 py-3 font-medium">Operation</th>
                <th className="px-6 py-3 font-medium">Timestamp</th>
                <th className="px-6 py-3 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {['Note', 'Card', 'DeckSettings'].map((entity, i) => (
                <tr key={i} className="hover:bg-accent/50">
                  <td className="px-6 py-3 font-medium">{entity}</td>
                  <td className="px-6 py-3"><span className="bg-blue-500/10 text-blue-500 px-2 py-0.5 rounded text-xs">Update</span></td>
                  <td className="px-6 py-3 text-muted-foreground">Oct 24, 14:0{i}</td>
                  <td className="px-6 py-3 text-right">
                    {i === 0 ? <span className="text-amber-500 flex items-center justify-end gap-1"><CloudUpload size={14}/> Pending</span> : <span className="text-green-500 flex items-center justify-end gap-1"><Cloud size={14}/> Synced</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Sync Engine Scaffolding complete.")

