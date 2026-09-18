import os
import json
from pathlib import Path

base = Path('.')

dirs = [
    'src-tauri/src/infrastructure/repositories',
    'src-tauri/src/commands/editor',
    'src/features/editor/components/tiptap',
    'src/features/editor/hooks',
    'src/features/editor/api',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. Update package.json for advanced Tiptap extensions
pkg_path = base / 'package.json'
if pkg_path.exists():
    try:
        pkg = json.loads(pkg_path.read_text())
        pkg['dependencies'].update({
            "@tiptap/extension-table": "^2.2.4",
            "@tiptap/extension-table-row": "^2.2.4",
            "@tiptap/extension-table-cell": "^2.2.4",
            "@tiptap/extension-table-header": "^2.2.4",
            "@tiptap/extension-code-block-lowlight": "^2.2.4",
            "@tiptap/extension-link": "^2.2.4",
            "@tiptap/extension-character-count": "^2.2.4",
            "lowlight": "^3.1.0"
        })
        pkg_path.write_text(json.dumps(pkg, indent=2))
    except Exception:
        pass

# 2. Rust Repositories
scripts['src-tauri/src/infrastructure/repositories/mod.rs'] = r'''pub mod note_repository;
pub mod card_repository;
pub mod media_repository;
'''

scripts['src-tauri/src/infrastructure/repositories/note_repository.rs'] = r'''use rusqlite::{params, Connection, Transaction};
use crate::domain::note::Note;

pub fn save_note_tx(tx: &Transaction, note: &Note) -> Result<(), rusqlite::Error> {
    tx.execute(
        "INSERT OR REPLACE INTO notes (id, deck_id, note_type, content, created_at) 
         VALUES (?1, ?2, ?3, ?4, ?5)",
        params![note.id, note.deck_id, note.note_type, note.content, note.created_at],
    )?;
    
    // Future FTS extraction logic would go here
    Ok(())
}
'''

scripts['src-tauri/src/infrastructure/repositories/card_repository.rs'] = r'''use rusqlite::{params, Connection, Transaction};
use crate::domain::card::Card;

pub fn save_card_tx(tx: &Transaction, card: &Card) -> Result<(), rusqlite::Error> {
    tx.execute(
        "INSERT OR REPLACE INTO cards (id, note_id, due_date, interval, ease_factor, reps, lapses, state) 
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
        params![card.id, card.note_id, card.due_date, card.interval, card.ease_factor, card.reps, card.lapses, card.state],
    )?;
    Ok(())
}

pub fn delete_cards_by_note_tx(tx: &Transaction, note_id: &str) -> Result<(), rusqlite::Error> {
    tx.execute("DELETE FROM cards WHERE note_id = ?1", params![note_id])?;
    Ok(())
}
'''

# 3. Save Note Command (The Transaction Pipeline)
scripts['src-tauri/src/commands/editor/save_commands.rs'] = r'''use tauri::State;
use uuid::Uuid;
use chrono::Utc;
use std::collections::HashMap;
use crate::db::connection::DbState;
use crate::domain::note::Note;
use crate::domain::card::Card;
use crate::domain::editor::note_type::NoteType;
use crate::application::editor::card_generator::CardGenerator;
use crate::infrastructure::repositories::{note_repository, card_repository};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct SaveNoteRequest {
    pub note_id: Option<String>,
    pub deck_id: String,
    pub note_type: NoteType,
    pub content_json: String, // Tiptap JSON Document containing all fields
    pub fields_map: HashMap<String, String>, // Extracted fields for Handlebars generation
}

#[derive(Serialize)]
pub struct SaveNoteResponse {
    pub note_id: String,
    pub cards_generated: usize,
}

#[tauri::command]
pub fn save_note(request: SaveNoteRequest, state: State<DbState>) -> Result<SaveNoteResponse, String> {
    let mut conn_guard = state.conn.lock().unwrap();
    let tx = conn_guard.transaction().map_err(|e| e.to_string())?;

    let note_id = request.note_id.unwrap_or_else(|| Uuid::new_v4().to_string());
    
    // 1. Validation (Mocked for now)
    if request.fields_map.is_empty() {
        return Err("Note must contain at least one field".to_string());
    }

    // 2. Generate Cards via Application Engine
    let generator = CardGenerator::new();
    let previews = generator.generate_preview(&request.note_type, &request.fields_map)?;
    
    let note = Note {
        id: note_id.clone(),
        deck_id: request.deck_id,
        note_type: request.note_type.id.clone(),
        content: request.content_json,
        created_at: Utc::now().timestamp(),
    };

    // 3. Store Note
    note_repository::save_note_tx(&tx, &note).map_err(|e| e.to_string())?;

    // 4. Store Cards
    // First clear existing cards for this note to handle template removals
    card_repository::delete_cards_by_note_tx(&tx, &note_id).map_err(|e| e.to_string())?;
    
    for preview in &previews {
        let card = Card {
            id: Uuid::new_v4().to_string(),
            note_id: note_id.clone(),
            due_date: 0,
            interval: 0,
            ease_factor: 2.5,
            reps: 0,
            lapses: 0,
            state: 0, // New
        };
        card_repository::save_card_tx(&tx, &card).map_err(|e| e.to_string())?;
    }

    // 5. Commit Transaction
    tx.commit().map_err(|e| e.to_string())?;

    Ok(SaveNoteResponse {
        note_id,
        cards_generated: previews.len(),
    })
}
'''

# 4. React Advanced Tiptap Editor & Autosave
scripts['src/features/editor/components/tiptap/AdvancedEditor.tsx'] = r'''import React, { useEffect, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Image from '@tiptap/extension-image';
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import Link from '@tiptap/extension-link';
import CharacterCount from '@tiptap/extension-character-count';

interface AdvancedEditorProps {
  initialContent: any; // JSON
  onChange: (json: any) => void;
  placeholder?: string;
}

export function AdvancedEditor({ initialContent, onChange, placeholder }: AdvancedEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder: placeholder || "Type '/' for commands..." }),
      Image,
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      Link.configure({ openOnClick: false }),
      CharacterCount,
    ],
    content: initialContent,
    onUpdate: ({ editor }) => {
      onChange(editor.getJSON());
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm dark:prose-invert max-w-none focus:outline-none min-h-[150px] w-full p-4',
      },
      handleDrop: (view, event, slice, moved) => {
        // Intercept image drops here to hash and save via Tauri FS API, 
        // then insert a media reference node.
        return false;
      },
    },
  });

  if (!editor) return null;

  return (
    <div className="border border-border rounded-md focus-within:ring-1 focus-within:ring-primary overflow-hidden bg-card transition-all flex flex-col h-full">
      <div className="bg-muted/30 border-b border-border p-1.5 flex gap-1 flex-wrap shrink-0">
        <button onClick={() => editor.chain().focus().toggleBold().run()} className="px-2 py-1 text-xs hover:bg-accent rounded">B</button>
        <button onClick={() => editor.chain().focus().toggleItalic().run()} className="px-2 py-1 text-xs hover:bg-accent rounded">I</button>
        <button onClick={() => editor.chain().focus().toggleCodeBlock().run()} className="px-2 py-1 text-xs hover:bg-accent rounded">Code</button>
        <button onClick={() => editor.chain().focus().toggleBlockquote().run()} className="px-2 py-1 text-xs hover:bg-accent rounded">Quote</button>
        <div className="flex-1"></div>
        <div className="text-[10px] text-muted-foreground self-center px-2">
          {editor.storage.characterCount.words()} words
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        <EditorContent editor={editor} className="h-full" />
      </div>
    </div>
  );
}
'''

scripts['src/features/editor/hooks/useAutosave.ts'] = r'''import { useEffect, useRef, useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

export function useAutosave(data: any, saveFn: (data: any) => Promise<any>, delay = 2000) {
  const [status, setStatus] = useState<'saved' | 'saving' | 'error' | 'unsaved'>('saved');
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    setStatus('unsaved');

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(async () => {
      setStatus('saving');
      try {
        await saveFn(data);
        setStatus('saved');
      } catch (err) {
        console.error("Autosave failed:", err);
        setStatus('error');
      }
    }, delay);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [data, delay, saveFn]);

  return status;
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Feature Editor Scaffolding complete.")

