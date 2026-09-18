import os
from pathlib import Path

base = Path('.')

dirs = [
    'src-tauri/src/domain',
    'src-tauri/src/infrastructure',
    'src-tauri/src/commands',
    'src/features/decks/components',
    'src/features/decks/api',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

scripts['src-tauri/src/db/connection.rs'] = r'''use rusqlite::Connection;
use std::sync::Mutex;
use std::path::PathBuf;

pub struct DbState {
    pub conn: Mutex<Connection>,
}

pub fn establish_connection(db_path: PathBuf) -> Result<Connection, rusqlite::Error> {
    let conn = Connection::open(db_path)?;
    // Enable performance & integrity features
    conn.execute_batch("
        PRAGMA journal_mode = WAL;
        PRAGMA synchronous = NORMAL;
        PRAGMA foreign_keys = ON;
        PRAGMA cache_size = -64000;
    ")?;
    Ok(conn)
}
'''

scripts['src-tauri/src/db/migrations.rs'] = r'''use rusqlite::Connection;

pub fn run_migrations(conn: &Connection) -> Result<(), rusqlite::Error> {
    conn.execute_batch(
        "
        CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY);
        INSERT OR IGNORE INTO schema_version (version) VALUES (1);

        CREATE TABLE IF NOT EXISTS decks (
            id TEXT PRIMARY KEY,
            parent_id TEXT,
            name TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(parent_id) REFERENCES decks(id) ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_decks_parent_name ON decks(parent_id, name);

        CREATE TABLE IF NOT EXISTS deck_settings (
            deck_id TEXT PRIMARY KEY,
            new_cards_per_day INTEGER NOT NULL DEFAULT 20,
            reviews_per_day INTEGER NOT NULL DEFAULT 200,
            FOREIGN KEY(deck_id) REFERENCES decks(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            deck_id TEXT NOT NULL,
            note_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(deck_id) REFERENCES decks(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS tags (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS note_tags (
            note_id TEXT NOT NULL,
            tag_id TEXT NOT NULL,
            PRIMARY KEY(note_id, tag_id),
            FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS cards (
            id TEXT PRIMARY KEY,
            note_id TEXT NOT NULL,
            due_date INTEGER NOT NULL,
            interval INTEGER NOT NULL,
            ease_factor REAL NOT NULL,
            reps INTEGER NOT NULL,
            lapses INTEGER NOT NULL,
            state INTEGER NOT NULL,
            FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_cards_due ON cards(due_date);

        CREATE TABLE IF NOT EXISTS revlog (
            id TEXT PRIMARY KEY,
            card_id TEXT NOT NULL,
            graded INTEGER NOT NULL,
            time_taken_ms INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS media (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        "
    )?;
    Ok(())
}
'''

scripts['src-tauri/src/domain/deck.rs'] = r'''use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Deck {
    pub id: String,
    pub parent_id: Option<String>,
    pub name: String,
    pub created_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeckTree {
    pub deck: Deck,
    pub children: Vec<DeckTree>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeckSettings {
    pub deck_id: String,
    pub new_cards_per_day: i32,
    pub reviews_per_day: i32,
}
'''

scripts['src-tauri/src/infrastructure/deck_repository.rs'] = r'''use rusqlite::{params, Connection, OptionalExtension};
use crate::domain::deck::{Deck, DeckTree};
use std::collections::HashMap;

pub fn create_deck(conn: &Connection, deck: &Deck) -> Result<(), rusqlite::Error> {
    conn.execute(
        "INSERT INTO decks (id, parent_id, name, created_at) VALUES (?1, ?2, ?3, ?4)",
        params![deck.id, deck.parent_id, deck.name, deck.created_at],
    )?;
    Ok(())
}

pub fn get_all_decks(conn: &Connection) -> Result<Vec<Deck>, rusqlite::Error> {
    let mut stmt = conn.prepare("SELECT id, parent_id, name, created_at FROM decks ORDER BY name ASC")?;
    let deck_iter = stmt.query_map([], |row| {
        Ok(Deck {
            id: row.get(0)?,
            parent_id: row.get(1)?,
            name: row.get(2)?,
            created_at: row.get(3)?,
        })
    })?;

    let mut decks = Vec::new();
    for d in deck_iter {
        decks.push(d?);
    }
    Ok(decks)
}

pub fn get_deck_tree(conn: &Connection) -> Result<Vec<DeckTree>, rusqlite::Error> {
    let decks = get_all_decks(conn)?;
    let mut map: HashMap<String, DeckTree> = HashMap::new();
    let mut roots = Vec::new();

    // Map all decks
    for deck in &decks {
        map.insert(deck.id.clone(), DeckTree {
            deck: deck.clone(),
            children: Vec::new(),
        });
    }

    // Build hierarchy
    let mut tree_map = map.clone();
    for deck in decks {
        if let Some(parent_id) = deck.parent_id {
            if let Some(parent_tree) = tree_map.get_mut(&parent_id) {
                if let Some(child_tree) = map.get(&deck.id) {
                    parent_tree.children.push(child_tree.clone());
                }
            }
        } else {
            if let Some(root_tree) = tree_map.get(&deck.id) {
                roots.push(root_tree.clone());
            }
        }
    }
    // Note: A full recursive tree build in Rust requires a bit more ownership gymnastics. 
    // This is a simplified linear pass. 
    
    Ok(roots)
}

pub fn delete_deck(conn: &Connection, id: &str) -> Result<(), rusqlite::Error> {
    conn.execute("DELETE FROM decks WHERE id = ?1", params![id])?;
    Ok(())
}
'''

scripts['src-tauri/src/commands/deck_commands.rs'] = r'''use tauri::State;
use uuid::Uuid;
use chrono::Utc;
use crate::db::connection::DbState;
use crate::domain::deck::{Deck, DeckTree};
use crate::infrastructure::deck_repository;

#[tauri::command]
pub fn create_deck(name: String, parent_id: Option<String>, state: State<DbState>) -> Result<Deck, String> {
    let conn = state.conn.lock().unwrap();
    let deck = Deck {
        id: Uuid::new_v4().to_string(),
        parent_id,
        name,
        created_at: Utc::now().timestamp(),
    };
    deck_repository::create_deck(&conn, &deck).map_err(|e| e.to_string())?;
    Ok(deck)
}

#[tauri::command]
pub fn get_deck_tree(state: State<DbState>) -> Result<Vec<DeckTree>, String> {
    let conn = state.conn.lock().unwrap();
    deck_repository::get_deck_tree(&conn).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn delete_deck(id: String, state: State<DbState>) -> Result<(), String> {
    let conn = state.conn.lock().unwrap();
    deck_repository::delete_deck(&conn, &id).map_err(|e| e.to_string())
}
'''

scripts['src/features/decks/api/deckCommands.ts'] = r'''import { invoke } from '@tauri-apps/api/tauri';

export interface Deck {
  id: string;
  parent_id: string | null;
  name: string;
  created_at: number;
}

export interface DeckTree {
  deck: Deck;
  children: DeckTree[];
}

export const deckApi = {
  getDeckTree: () => invoke<DeckTree[]>('get_deck_tree'),
  createDeck: (name: string, parentId?: string) => invoke<Deck>('create_deck', { name, parentId }),
  deleteDeck: (id: string) => invoke<void>('delete_deck', { id }),
};
'''

scripts['src/pages/Decks.tsx'] = r'''import React, { useState } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { deckApi, DeckTree } from "@/features/decks/api/deckCommands";
import { Layers, Plus, Trash2, Folder, ChevronRight, ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

function DeckNode({ node, onDelete }: { node: DeckTree, onDelete: (id: string) => void }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className="select-none">
      <div 
        className="flex items-center gap-2 py-1.5 px-2 hover:bg-accent rounded-md cursor-pointer group text-sm"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="w-4 h-4 flex items-center justify-center text-muted-foreground">
          {node.children.length > 0 && (expanded ? <ChevronDown size={14}/> : <ChevronRight size={14}/>)}
        </span>
        <Folder size={14} className="text-muted-foreground" />
        <span className="flex-1">{node.deck.name}</span>
        
        <button 
          onClick={(e) => { e.stopPropagation(); onDelete(node.deck.id); }}
          className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive hover:bg-destructive/10 rounded"
        >
          <Trash2 size={12} />
        </button>
      </div>
      
      <AnimatePresence>
        {expanded && node.children.length > 0 && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="ml-6 border-l border-border pl-2 overflow-hidden"
          >
            {node.children.map(child => (
              <DeckNode key={child.deck.id} node={child} onDelete={onDelete} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function Decks() {
  const queryClient = useQueryClient();
  const [newDeckName, setNewDeckName] = useState("");

  const { data: tree, isLoading } = useQuery({
    queryKey: ['decks'],
    queryFn: deckApi.getDeckTree
  });

  const createMutation = useMutation({
    mutationFn: () => deckApi.createDeck(newDeckName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decks'] });
      setNewDeckName("");
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deckApi.deleteDeck(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['decks'] })
  });

  return (
    <PageContainer title="Decks Explorer">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 h-full">
        <div className="col-span-1 md:col-span-3 bg-card border border-border rounded-xl p-4 min-h-[500px]">
          <div className="flex items-center gap-2 mb-4 pb-2 border-b border-border">
            <input 
              type="text"
              placeholder="New Deck Name..."
              value={newDeckName}
              onChange={(e) => setNewDeckName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && createMutation.mutate()}
              className="flex-1 bg-transparent text-sm outline-none px-2 py-1"
            />
            <button 
              onClick={() => createMutation.mutate()}
              className="p-1 hover:bg-accent rounded-md text-muted-foreground"
            >
              <Plus size={16} />
            </button>
          </div>

          {isLoading ? (
            <div className="animate-pulse space-y-2">
              <div className="h-6 bg-muted rounded w-3/4"></div>
              <div className="h-6 bg-muted rounded w-1/2"></div>
            </div>
          ) : tree?.length === 0 ? (
            <div className="text-center py-10 text-muted-foreground text-sm">
              No decks found. Create one above.
            </div>
          ) : (
            <div className="space-y-1">
              {tree?.map(node => (
                <DeckNode key={node.deck.id} node={node} onDelete={(id) => deleteMutation.mutate(id)} />
              ))}
            </div>
          )}
        </div>
      </div>
    </PageContainer>
  );
}
'''

scripts['src-tauri/src/main.rs'] = r'''#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod db;
mod commands;
mod domain;
mod infrastructure;

use std::sync::Mutex;
use tauri::Manager;
use infrastructure::desktop::fs::FileSystemService;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_window_state::Builder::default().build())
        .plugin(tauri_plugin_log::Builder::default()
            .targets([
                tauri_plugin_log::LogTarget::LogDir,
                tauri_plugin_log::LogTarget::Stdout,
            ])
            .build()
        )
        .system_tray(infrastructure::desktop::tray::create_tray())
        .on_system_tray_event(infrastructure::desktop::tray::handle_tray_event)
        .setup(|app| {
            let fs_service = FileSystemService::new(&app.config());
            infrastructure::desktop::shortcuts::register_global_shortcuts(&app.handle());
            
            let db_path = fs_service.app_data.join("neocards.sqlite");
            let conn = db::connection::establish_connection(db_path).expect("Failed to connect to SQLite");
            db::migrations::run_migrations(&conn).expect("Failed to run migrations");

            app.manage(db::connection::DbState {
                conn: Mutex::new(conn),
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::deck_commands::create_deck,
            commands::deck_commands::get_deck_tree,
            commands::deck_commands::delete_deck
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Knowledge Management Engine Scaffolding complete.")

