import os
import json
from pathlib import Path

base = Path('.')

dirs = [
    'src-tauri/src/domain/editor',
    'src-tauri/src/application/editor',
    'src-tauri/src/commands/editor',
    'src/features/editor/components/tiptap',
    'src/features/editor/components/panels',
    'src/features/editor/api',
    'src/pages/editor',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. Update package.json to include Tiptap dependencies
pkg_path = base / 'package.json'
if pkg_path.exists():
    try:
        pkg = json.loads(pkg_path.read_text())
        pkg['dependencies'].update({
            "@tiptap/react": "^2.2.4",
            "@tiptap/starter-kit": "^2.2.4",
            "@tiptap/extension-placeholder": "^2.2.4",
            "@tiptap/extension-image": "^2.2.4",
            "@tiptap/extension-task-list": "^2.2.4",
            "@tiptap/extension-task-item": "^2.2.4",
            "handlebars": "^4.7.8" # For frontend-side template preview if needed, though Rust handles generation
        })
        pkg_path.write_text(json.dumps(pkg, indent=2))
    except Exception:
        pass

# 2. Rust Cargo.toml update to include handlebars and regex
cargo_path = base / 'src-tauri/Cargo.toml'
if cargo_path.exists():
    cargo = cargo_path.read_text()
    if 'handlebars' not in cargo:
        cargo = cargo.replace('[dependencies]', '[dependencies]\nhandlebars = "4.5.0"\nregex = "1.10.3"\n')
        cargo_path.write_text(cargo)

# 3. Rust Domain Models
scripts['src-tauri/src/domain/editor/note_type.rs'] = r'''use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NoteType {
    pub id: String,
    pub name: String,
    pub fields: Vec<FieldDefinition>,
    pub templates: Vec<CardTemplate>,
    pub created_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FieldDefinition {
    pub id: String,
    pub name: String,
    pub order: i32,
    pub required: bool,
    pub r#type: String, // e.g., "Text", "Image", "Audio"
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CardTemplate {
    pub id: String,
    pub name: String,
    pub front_html: String,
    pub back_html: String,
    pub css: String,
}
'''

# 4. Rust Card Generation Engine (Application Layer)
scripts['src-tauri/src/application/editor/card_generator.rs'] = r'''use std::collections::HashMap;
use handlebars::Handlebars;
use crate::domain::editor::note_type::{NoteType, CardTemplate};
use crate::domain::card::Card;

pub struct GeneratedPreview {
    pub template_id: String,
    pub template_name: String,
    pub front_compiled: String,
    pub back_compiled: String,
}

pub struct CardGenerator<'a> {
    registry: Handlebars<'a>,
}

impl<'a> CardGenerator<'a> {
    pub fn new() -> Self {
        let mut registry = Handlebars::new();
        // Disable HTML escaping to allow rich text fields to render natively
        registry.register_escape_fn(handlebars::no_escape);
        Self { registry }
    }

    /// Evaluates templates against the provided fields map. 
    /// Returns the compiled HTML previews. React will render these.
    pub fn generate_preview(&self, note_type: &NoteType, fields: &HashMap<String, String>) -> Result<Vec<GeneratedPreview>, String> {
        let mut previews = Vec::new();

        for template in &note_type.templates {
            // Check conditional: Anki standard is if Front is empty, do not generate card.
            // A robust implementation would use AST parsing, but for Milestone 3, we leverage Handlebars.
            let front_compiled = self.registry.render_template(&template.front_html, fields).map_err(|e| e.to_string())?;
            let back_compiled = self.registry.render_template(&template.back_html, fields).map_err(|e| e.to_string())?;

            if !front_compiled.trim().is_empty() {
                previews.push(GeneratedPreview {
                    template_id: template.id.clone(),
                    template_name: template.name.clone(),
                    front_compiled,
                    back_compiled,
                });
            }
        }

        Ok(previews)
    }
}
'''

# 5. Rust IPC Commands
scripts['src-tauri/src/commands/editor/preview_commands.rs'] = r'''use tauri::State;
use std::collections::HashMap;
use crate::db::connection::DbState;
use crate::domain::editor::note_type::NoteType;
use crate::application::editor::card_generator::{CardGenerator, GeneratedPreview};
use serde::{Serialize, Deserialize};

#[derive(Deserialize)]
pub struct PreviewRequest {
    pub note_type: NoteType,
    pub fields: HashMap<String, String>,
}

#[tauri::command]
pub fn preview_cards_live(request: PreviewRequest) -> Result<Vec<GeneratedPreview>, String> {
    let generator = CardGenerator::new();
    // In production, validation engine would run here before generation
    generator.generate_preview(&request.note_type, &request.fields)
}
'''

# 6. React Tiptap Editor
scripts['src/features/editor/components/tiptap/RichTextEditor.tsx'] = r'''import React, { useEffect } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';

interface RichTextEditorProps {
  content: string;
  onChange: (content: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

export function RichTextEditor({ content, onChange, placeholder, autoFocus }: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder: placeholder || "Type '/' for commands..." }),
    ],
    content,
    autofocus: autoFocus,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm dark:prose-invert max-w-none focus:outline-none min-h-[100px] w-full p-3 bg-transparent',
      },
    },
  });

  useEffect(() => {
    if (editor && editor.getHTML() !== content) {
      editor.commands.setContent(content, false);
    }
  }, [content, editor]);

  if (!editor) return null;

  return (
    <div className="border border-border rounded-md focus-within:ring-1 focus-within:ring-primary overflow-hidden bg-card transition-all">
      <div className="bg-muted/50 border-b border-border p-1.5 flex gap-1">
        {/* Placeholder toolbar: B, I, Code, Math */}
        <button className="px-2 py-1 text-xs font-medium rounded hover:bg-muted text-muted-foreground">B</button>
        <button className="px-2 py-1 text-xs font-medium rounded hover:bg-muted text-muted-foreground">I</button>
      </div>
      <EditorContent editor={editor} />
    </div>
  );
}
'''

# 7. Editor Layout Shell
scripts['src/features/editor/components/panels/EditorShell.tsx'] = r'''import React, { useState } from 'react';
import { RichTextEditor } from '../tiptap/RichTextEditor';
import { useQuery } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/tauri';
import { Save, Layout, Settings } from 'lucide-react';
import { motion } from 'framer-motion';

// Mocked NoteType for Milestone 3 UI
const MOCK_NOTE_TYPE = {
  id: "basic-1",
  name: "Basic",
  fields: [{ id: "f1", name: "Front", order: 1, required: true, type: "Text" }, { id: "f2", name: "Back", order: 2, required: false, type: "Text" }],
  templates: [{ id: "t1", name: "Card 1", front_html: "{{Front}}", back_html: "{{Front}}<hr id=answer>{{Back}}", css: ".card { text-align: center; }" }],
  created_at: Date.now()
};

export function EditorShell() {
  const [fields, setFields] = useState<Record<string, string>>({ "Front": "", "Back": "" });

  const { data: previews } = useQuery({
    queryKey: ['card-preview', fields],
    queryFn: () => invoke('preview_cards_live', { request: { note_type: MOCK_NOTE_TYPE, fields } }),
    // Debounce fast typing
    staleTime: 100,
  });

  return (
    <div className="flex h-full overflow-hidden bg-background">
      {/* LEFT: Field Editor Panel */}
      <div className="flex-1 flex flex-col border-r border-border overflow-y-auto">
        <div className="h-12 border-b border-border flex items-center px-4 justify-between bg-card shrink-0">
          <div className="font-medium text-sm">Add Note: Basic</div>
          <div className="flex gap-2">
            <button className="p-1.5 hover:bg-accent rounded text-muted-foreground"><Settings size={16}/></button>
          </div>
        </div>
        
        <div className="p-6 space-y-6 flex-1">
          {MOCK_NOTE_TYPE.fields.map(field => (
            <div key={field.id} className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex justify-between">
                <span>{field.name}</span>
                {field.required && <span className="text-destructive">*</span>}
              </label>
              <RichTextEditor 
                content={fields[field.name]}
                onChange={(html) => setFields(prev => ({...prev, [field.name]: html}))}
              />
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-border bg-card flex justify-end gap-2 shrink-0">
          <button className="px-4 py-2 text-sm font-medium border border-border rounded-md hover:bg-accent">Cancel</button>
          <button className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md flex items-center gap-2">
            <Save size={16} /> Save Note
          </button>
        </div>
      </div>

      {/* RIGHT: Live Preview Panel */}
      <div className="w-[400px] flex flex-col bg-muted/20 shrink-0">
        <div className="h-12 border-b border-border flex items-center px-4 gap-2 bg-card">
          <Layout size={16} className="text-muted-foreground" />
          <div className="font-medium text-sm">Live Preview</div>
        </div>
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {previews && Array.isArray(previews) && previews.map((preview: any) => (
            <motion.div initial={{opacity:0}} animate={{opacity:1}} key={preview.template_id} className="space-y-3">
              <div className="text-xs font-medium text-muted-foreground uppercase">{preview.template_name}</div>
              <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden divide-y divide-border">
                <div className="p-4 min-h-[100px] flex items-center justify-center" dangerouslySetInnerHTML={{__html: preview.front_compiled}}></div>
                <div className="p-4 min-h-[100px] flex items-center justify-center bg-muted/10" dangerouslySetInnerHTML={{__html: preview.back_compiled}}></div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Editor Engine Scaffolding complete.")

