import os
import json
from pathlib import Path

base = Path('.')

dirs = [
    'src-tauri/src/db',
    'src-tauri/src/commands/browser',
    'src/features/browser/components',
    'src/features/browser/api',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. Update Package.json for virtualized grid
pkg_path = base / 'package.json'
if pkg_path.exists():
    try:
        pkg = json.loads(pkg_path.read_text())
        pkg['dependencies'].update({
            "@tanstack/react-virtual": "^3.1.2",
            "@tanstack/react-table": "^8.15.0"
        })
        pkg_path.write_text(json.dumps(pkg, indent=2))
    except Exception:
        pass

# 2. Rust FTS Pipeline
scripts['src-tauri/src/db/fts.rs'] = r'''use rusqlite::{Connection, params};

/// Initializes the FTS5 virtual tables for the document engine.
/// We strictly index plain text extracted from the JSON AST, never HTML.
pub fn setup_fts_tables(conn: &Connection) -> Result<(), rusqlite::Error> {
    conn.execute_batch(
        "
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
            note_id UNINDEXED,
            deck_id UNINDEXED,
            content,
            tags,
            tokenize = 'porter unicode61'
        );

        -- Trigger to automatically push text into FTS when a note is inserted.
        -- In a robust system, the JSON->Text extraction should happen in Rust before INSERT,
        -- but SQLite JSON functions can be used for basic extraction.
        -- We assume Rust extracts the `plain_text` and inserts it alongside the JSON, 
        -- or Rust directly inserts into `notes_fts` within the save transaction.
        "
    )?;
    Ok(())
}

/// Helper function to traverse the Tiptap JSON AST and extract pure text for search
pub fn extract_text_from_json_ast(json_str: &str) -> String {
    // MOCK: In production, parse JSON and recursively extract the 'text' fields 
    // from paragraphs, headings, blockquotes, ignoring marks and structure.
    "extracted plain text string".to_string()
}
'''

# 3. Rust Browser IPC Commands
scripts['src-tauri/src/commands/browser/mod.rs'] = r'''pub mod search_commands;
'''

scripts['src-tauri/src/commands/browser/search_commands.rs'] = r'''use tauri::State;
use crate::db::connection::DbState;
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct SearchQuery {
    pub query: String,
    pub deck_id: Option<String>,
    pub limit: u32,
    pub offset: u32,
}

#[derive(Serialize)]
pub struct SearchResult {
    pub note_id: String,
    pub snippet: String,
    pub deck_name: String,
    pub card_states: Vec<i32>,
}

#[tauri::command]
pub fn search_notes(query: SearchQuery, state: State<DbState>) -> Result<Vec<SearchResult>, String> {
    let conn = state.conn.lock().unwrap();
    
    // MOCK: Execute FTS5 match query
    // SELECT note_id, snippet(notes_fts, -1, '<b>', '</b>', '...', 64) FROM notes_fts WHERE content MATCH ?
    
    Ok(vec![
        SearchResult {
            note_id: "mock-1".to_string(),
            snippet: "The <b>mitochondria</b> is the powerhouse...".to_string(),
            deck_name: "Biology".to_string(),
            card_states: vec![2, 1], // Review, Learning
        }
    ])
}

#[derive(Deserialize)]
pub struct BulkActionRequest {
    pub note_ids: Vec<String>,
    pub action: String, // "delete", "suspend", "change_deck"
    pub payload: Option<String>,
}

#[tauri::command]
pub fn execute_bulk_action(req: BulkActionRequest, state: State<DbState>) -> Result<usize, String> {
    let mut conn = state.conn.lock().unwrap();
    let tx = conn.transaction().map_err(|e| e.to_string())?;
    // Execute bulk SQL update/delete
    tx.commit().map_err(|e| e.to_string())?;
    Ok(req.note_ids.len())
}
'''

# 4. React Browser Layout
scripts['src/features/browser/components/BrowserLayout.tsx'] = r'''import React, { useState } from 'react';
import { Search, Filter, Tag, Layers, Star, Database } from 'lucide-react';
import { VirtualizedGrid } from './VirtualizedGrid';

export function BrowserLayout() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="flex h-full w-full bg-background overflow-hidden">
      
      {/* LEFT PANEL: Navigator */}
      <div className="w-64 border-r border-border bg-card/50 flex flex-col shrink-0">
        <div className="p-4 border-b border-border">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search anything..." 
              className="w-full bg-background border border-border rounded-md pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-4">
          <div>
            <div className="text-xs font-semibold text-muted-foreground uppercase px-2 mb-1">Collections</div>
            <div className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded cursor-pointer"><Layers size={14}/> All Notes</div>
            <div className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded cursor-pointer"><Star size={14}/> Favorites</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-muted-foreground uppercase px-2 mb-1">Tags</div>
            <div className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded cursor-pointer"><Tag size={14}/> #biology</div>
            <div className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded cursor-pointer"><Tag size={14}/> #spanish</div>
          </div>
        </div>
      </div>

      {/* CENTER PANEL: Grid */}
      <div className="flex-1 flex flex-col min-w-0 bg-background">
        <div className="h-12 border-b border-border flex items-center px-4 justify-between bg-card">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Database size={16} className="text-muted-foreground" />
            142,091 Notes Found
          </div>
          <div className="flex gap-2">
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm border border-border rounded-md hover:bg-accent">
              <Filter size={14} /> Filter
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-hidden">
          <VirtualizedGrid query={searchQuery} />
        </div>
      </div>

      {/* RIGHT PANEL: Inspector */}
      <div className="w-80 border-l border-border bg-card/50 flex flex-col shrink-0 hidden lg:flex">
        <div className="h-12 border-b border-border flex items-center px-4 font-medium text-sm">
          Inspector
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          <div className="space-y-2">
            <div className="text-xs font-semibold text-muted-foreground uppercase">Note Metadata</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-muted-foreground">Type</div><div>Basic</div>
              <div className="text-muted-foreground">Deck</div><div>Biology</div>
              <div className="text-muted-foreground">Created</div><div>Oct 24, 2024</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-xs font-semibold text-muted-foreground uppercase">FSRS Memory State</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-muted-foreground">Stability</div><div className="text-green-500">84.2%</div>
              <div className="text-muted-foreground">Difficulty</div><div>4.1</div>
              <div className="text-muted-foreground">Interval</div><div>21 days</div>
              <div className="text-muted-foreground">Lapses</div><div>0</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
'''

# 5. React Virtualized Grid
scripts['src/features/browser/components/VirtualizedGrid.tsx'] = r'''import React, { useRef } from 'react';

// For Milestone 6, we scaffold the visual representation.
// In production, this uses @tanstack/react-virtual and @tanstack/react-table
export function VirtualizedGrid({ query }: { query: string }) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // MOCK DATA
  const rows = Array.from({ length: 50 }).map((_, i) => ({
    id: i,
    deck: "Biology",
    front: `Mitochondria ${i}`,
    due: "2024-11-01",
    state: "Review"
  }));

  return (
    <div ref={scrollRef} className="h-full w-full overflow-auto relative">
      <table className="w-full text-left border-collapse text-sm whitespace-nowrap">
        <thead className="sticky top-0 bg-card z-10 shadow-sm">
          <tr>
            <th className="font-semibold p-3 border-b border-r border-border w-10 text-center"><input type="checkbox"/></th>
            <th className="font-semibold p-3 border-b border-r border-border">Sort Field</th>
            <th className="font-semibold p-3 border-b border-r border-border">Deck</th>
            <th className="font-semibold p-3 border-b border-r border-border">Due Date</th>
            <th className="font-semibold p-3 border-b border-border">State</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.id} className="hover:bg-accent/50 cursor-pointer border-b border-border transition-colors group">
              <td className="p-3 border-r border-border text-center"><input type="checkbox" className="opacity-0 group-hover:opacity-100" /></td>
              <td className="p-3 border-r border-border truncate max-w-xs">{row.front}</td>
              <td className="p-3 border-r border-border">{row.deck}</td>
              <td className="p-3 border-r border-border text-muted-foreground">{row.due}</td>
              <td className="p-3">
                <span className="px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 text-xs font-medium">{row.state}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
'''

# 6. Page
scripts['src/pages/Browse.tsx'] = r'''import React from "react";
import { BrowserLayout } from "@/features/browser/components/BrowserLayout";

export function Browse() {
  return (
    <div className="h-full w-full">
      <BrowserLayout />
    </div>
  );
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Browser Scaffolding complete.")

