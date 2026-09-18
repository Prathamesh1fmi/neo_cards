import os
from pathlib import Path

base = Path('.')

dirs = [
    'src-tauri/src/application/interop',
    'src-tauri/src/commands/interop',
    'src/features/interop/components',
    'src/features/interop/api',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. Rust Interop Architecture
scripts['src-tauri/src/application/interop/mod.rs'] = r'''pub mod importer;
pub mod exporter;
pub mod parsers;
pub mod media_sync;
'''

# 2. Importer Pipeline
scripts['src-tauri/src/application/interop/importer.rs'] = r'''use std::path::PathBuf;
use crate::domain::document::model::DocumentNode;
use crate::domain::note::Note;
use rusqlite::Transaction;

pub enum ConflictResolution {
    Replace,
    Merge,
    Skip,
    Rename,
    Duplicate,
}

pub struct ImportResult {
    pub notes_imported: usize,
    pub media_imported: usize,
    pub duplicates_skipped: usize,
}

/// Abstract Trait for all Importers (NeoCards, CSV, APKG, Markdown)
pub trait Importer {
    fn validate(&self, path: &PathBuf) -> Result<(), String>;
    fn parse(&self, path: &PathBuf) -> Result<Vec<Note>, String>;
    fn import(&self, path: &PathBuf, tx: &Transaction, resolution: ConflictResolution) -> Result<ImportResult, String>;
}

/// The core orchestration engine for safely importing data
pub struct ImportEngine;

impl ImportEngine {
    pub fn execute(importer: Box<dyn Importer>, path: &PathBuf, tx: &Transaction, resolution: ConflictResolution) -> Result<ImportResult, String> {
        importer.validate(path)?;
        // Execute the atomic import within the provided SQLite transaction
        importer.import(path, tx, resolution)
    }
}
'''

# 3. Exporter Pipeline
scripts['src-tauri/src/application/interop/exporter.rs'] = r'''use std::path::PathBuf;
use rusqlite::Connection;

/// Abstract Trait for all Exporters
pub trait Exporter {
    fn export(&self, conn: &Connection, destination: &PathBuf) -> Result<(), String>;
}

pub struct ExportEngine;

impl ExportEngine {
    pub fn execute(exporter: Box<dyn Exporter>, conn: &Connection, destination: &PathBuf) -> Result<(), String> {
        exporter.export(conn, destination)
    }
}
'''

# 4. Parsers Stub
scripts['src-tauri/src/application/interop/parsers.rs'] = r'''use crate::application::interop::importer::{Importer, ImportResult, ConflictResolution};
use std::path::PathBuf;
use rusqlite::Transaction;
use crate::domain::note::Note;

pub struct CsvImporter;
impl Importer for CsvImporter {
    fn validate(&self, _path: &PathBuf) -> Result<(), String> { Ok(()) }
    fn parse(&self, _path: &PathBuf) -> Result<Vec<Note>, String> { Ok(vec![]) }
    fn import(&self, _path: &PathBuf, _tx: &Transaction, _resolution: ConflictResolution) -> Result<ImportResult, String> {
        Ok(ImportResult { notes_imported: 0, media_imported: 0, duplicates_skipped: 0 })
    }
}

pub struct ApkgImporter;
impl Importer for ApkgImporter {
    fn validate(&self, _path: &PathBuf) -> Result<(), String> { Ok(()) }
    fn parse(&self, _path: &PathBuf) -> Result<Vec<Note>, String> { Ok(vec![]) }
    fn import(&self, _path: &PathBuf, _tx: &Transaction, _resolution: ConflictResolution) -> Result<ImportResult, String> {
        Ok(ImportResult { notes_imported: 0, media_imported: 0, duplicates_skipped: 0 })
    }
}
'''

# 5. Media Synchronization
scripts['src-tauri/src/application/interop/media_sync.rs'] = r'''use std::path::PathBuf;

pub struct MediaSyncEngine;

impl MediaSyncEngine {
    /// Hashes the incoming binary file via SHA-256. 
    /// If the hash already exists in `media_repository`, it skips copying to prevent bloat.
    /// Returns the exact hash string to inject into the Tiptap JSON AST.
    pub fn hash_and_store(binary_data: &[u8], media_dir: &PathBuf) -> Result<String, String> {
        // MOCK: calculate SHA256, write to media_dir if not exists
        Ok("hash12345".to_string())
    }
}
'''

# 6. IPC Commands & Progress Events
scripts['src-tauri/src/commands/interop/mod.rs'] = r'''pub mod interop_commands;'''

scripts['src-tauri/src/commands/interop/interop_commands.rs'] = r'''use tauri::{Window, State};
use crate::db::connection::DbState;
use std::path::PathBuf;
use crate::application::interop::{
    importer::{ImportEngine, ConflictResolution},
    parsers::CsvImporter,
};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct ImportRequest {
    pub file_path: String,
    pub format: String, // "csv", "apkg", "json"
    pub resolution: String, // "merge", "replace"
}

#[derive(Clone, Serialize)]
pub struct ProgressEvent {
    pub current: usize,
    pub total: usize,
    pub message: String,
}

#[tauri::command]
pub async fn start_import(req: ImportRequest, window: Window, state: State<'_, DbState>) -> Result<String, String> {
    let mut conn = state.conn.lock().unwrap();
    let tx = conn.transaction().map_err(|e| e.to_string())?;

    // Emit progress event to React
    let _ = window.emit("import_progress", ProgressEvent {
        current: 0,
        total: 100,
        message: "Validating file...".to_string(),
    });

    let path = PathBuf::from(&req.file_path);
    let importer = match req.format.as_str() {
        "csv" => Box::new(CsvImporter),
        _ => return Err("Unsupported format".to_string()),
    };

    let resolution = match req.resolution.as_str() {
        "replace" => ConflictResolution::Replace,
        _ => ConflictResolution::Merge,
    };

    // Execute atomic import
    match ImportEngine::execute(importer, &path, &tx, resolution) {
        Ok(result) => {
            tx.commit().map_err(|e| e.to_string())?;
            let _ = window.emit("import_progress", ProgressEvent {
                current: 100,
                total: 100,
                message: "Import complete.".to_string(),
            });
            Ok(format!("Imported {} notes successfully", result.notes_imported))
        }
        Err(e) => {
            // Transaction drops and rolls back automatically
            Err(format!("Import failed: {}", e))
        }
    }
}
'''

# 7. React Import Dialog UI
scripts['src/features/interop/components/ImportDialog.tsx'] = r'''import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import { FileUp, CheckCircle, AlertCircle } from 'lucide-react';

export function ImportDialog({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [filePath, setFilePath] = useState("");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<'idle' | 'importing' | 'success' | 'error'>('idle');

  useEffect(() => {
    const unlisten = listen('import_progress', (event: any) => {
      const { current, total, message } = event.payload;
      setProgress((current / total) * 100);
      setMessage(message);
    });
    return () => { unlisten.then(f => f()); };
  }, []);

  const handleImport = async () => {
    setStatus('importing');
    try {
      const result = await invoke('start_import', { 
        req: { file_path: filePath, format: 'csv', resolution: 'merge' } 
      });
      setMessage(result as string);
      setStatus('success');
    } catch (err: any) {
      setMessage(err);
      setStatus('error');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div className="w-[500px] bg-card border border-border shadow-2xl rounded-xl overflow-hidden flex flex-col">
        <div className="h-12 border-b border-border flex items-center px-4 font-medium">
          <FileUp size={16} className="mr-2 text-muted-foreground" /> Import Data
        </div>
        
        <div className="p-6 space-y-4 flex-1">
          {status === 'idle' && (
            <>
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase">File Path</label>
                <input 
                  type="text" 
                  value={filePath}
                  onChange={(e) => setFilePath(e.target.value)}
                  placeholder="C:\Downloads\deck.apkg"
                  className="w-full mt-1 border border-border bg-background px-3 py-2 text-sm rounded-md"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase">Conflict Resolution</label>
                <select className="w-full mt-1 border border-border bg-background px-3 py-2 text-sm rounded-md">
                  <option value="merge">Merge & Update Existing</option>
                  <option value="replace">Replace Existing</option>
                  <option value="skip">Skip Duplicates</option>
                </select>
              </div>
            </>
          )}

          {status === 'importing' && (
            <div className="py-8 text-center space-y-4">
              <div className="text-sm font-medium">{message}</div>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-primary transition-all duration-300" style={{ width: `${progress}%` }}></div>
              </div>
            </div>
          )}

          {status === 'success' && (
            <div className="py-8 text-center space-y-2">
              <CheckCircle size={48} className="mx-auto text-green-500" />
              <div className="font-semibold text-lg">Import Successful</div>
              <div className="text-sm text-muted-foreground">{message}</div>
            </div>
          )}

          {status === 'error' && (
            <div className="py-8 text-center space-y-2">
              <AlertCircle size={48} className="mx-auto text-destructive" />
              <div className="font-semibold text-lg text-destructive">Import Failed</div>
              <div className="text-sm text-muted-foreground">{message}</div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-border bg-muted/20 flex justify-end gap-2">
          {status !== 'importing' && (
            <button onClick={onClose} className="px-4 py-2 border border-border rounded-md text-sm hover:bg-accent font-medium">
              {status === 'success' || status === 'error' ? 'Close' : 'Cancel'}
            </button>
          )}
          {status === 'idle' && (
            <button onClick={handleImport} className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm hover:bg-primary/90 font-medium">
              Start Import
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Interoperability Platform Scaffolding complete.")

