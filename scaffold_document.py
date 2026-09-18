import os
from pathlib import Path

base = Path('.')

dirs = [
    'docs/adr',
    'src-tauri/src/domain/document',
    'src-tauri/src/application/document',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

docs = {}

docs['docs/adr/0005-document-engine.md'] = '''# ADR 0005: Document Engine

## Context
Our previous architecture treated HTML as the canonical data format for Notes. This is standard for web apps, but for a premium desktop application (like Obsidian or Notion), HTML destroys semantic meaning, makes Markdown/LaTeX parsing brittle, and breaks when migrating to mobile apps (React Native).

## Decision
We will build a dedicated Document Engine in Rust. The frontend (Tiptap) will act purely as an input mechanism. The Document Engine owns the Document Model (Blocks, Marks, Media References), Validation, Serialization, and the Rendering Orchestration.

## Consequences
- **Positive**: We have a strictly typed, semantic understanding of every note. We can easily extract text for FTS search, render native components on mobile, and write reliable plugins.
- **Negative**: Increased complexity. We must parse JSON ASTs in Rust and build a recursive rendering pipeline.
'''

docs['docs/adr/0006-json-storage-strategy.md'] = '''# ADR 0006: JSON Storage Strategy

## Context
Storing HTML directly in SQLite is space-efficient but structurally opaque.

## Decision
The canonical source of truth for all Note fields will be the ProseMirror / Tiptap JSON AST format. 
We will store this JSON string directly in the `notes.content` SQLite column.

## Consequences
- **Positive**: Perfectly preserves editor metadata, block types, marks, and media references. It allows unlimited undo history (since ProseMirror states are easily diffable JSON).
- **Negative**: JSON payload is slightly larger than raw HTML. FTS search requires a dedicated extraction step before saving.
'''

docs['docs/adr/0007-renderer-pipeline.md'] = '''# ADR 0007: Renderer Pipeline

## Context
If we store JSON, we need a way to convert it to HTML for the `WebView` preview and studying interfaces.

## Decision
We will implement a multi-stage Renderer Pipeline in Rust.
`JSON Document -> Markdown Renderer -> Math Renderer (KaTeX/MathJax) -> Media Renderer -> HTML Renderer -> Template Engine (Handlebars) -> Final Preview HTML`.

## Consequences
- **Positive**: Highly modular. If we switch math libraries or add syntax highlighting, we only update one pipeline stage. Security is enforced by a final sanitization step.
- **Negative**: Rendering a card requires multiple AST passes in Rust.
'''

docs['docs/adr/0008-media-architecture.md'] = '''# ADR 0008: Media Architecture

## Context
Storing Base64 images inside JSON documents bloats the database, degrades performance, and breaks sync algorithms.

## Decision
We will use Media Reference Objects. Binary files (Images, Audio, PDF) will be hashed (SHA-256) and saved to the local file system (`~/.neocards/media/`). The JSON document will only store a reference: `{ "type": "image", "attrs": { "hash": "abc123..." } }`.

## Consequences
- **Positive**: Notes remain kilobytes in size. SQLite stays lightning fast. Deduplication is automatic (same image pasted twice equals one file on disk).
- **Negative**: File system syncing is required alongside database syncing in the future.
'''

docs['docs/adr/0009-template-engine.md'] = '''# ADR 0009: Template Engine Boundaries

## Context
Handlebars was originally used to render the entire card preview directly from HTML fields.

## Decision
Handlebars will strictly be restricted to replacing Field Placeholders (`{{Front}}`). It will operate *after* the Renderer Pipeline has converted the JSON AST fields into secure HTML strings. Handlebars will not parse blocks or inline elements.

## Consequences
- **Positive**: Security boundary is clear. Template engine logic remains simple.
- **Negative**: Users cannot use Handlebars logic *inside* their notes, only inside the Card Templates.
'''

docs['src-tauri/src/domain/document/mod.rs'] = '''pub mod model;
'''

docs['src-tauri/src/domain/document/model.rs'] = '''use serde::{Serialize, Deserialize};
use std::collections::HashMap;

/// The canonical source of truth for a single field's content.
/// Represents a ProseMirror/Tiptap JSON AST.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DocumentNode {
    pub r#type: String, // "doc", "paragraph", "text", "image"
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub marks: Option<Vec<Mark>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub content: Option<Vec<DocumentNode>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub attrs: Option<HashMap<String, String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Mark {
    pub r#type: String, // "bold", "italic", "code"
    #[serde(skip_serializing_if = "Option::is_none")]
    pub attrs: Option<HashMap<String, String>>,
}
'''

docs['src-tauri/src/application/document/mod.rs'] = '''pub mod pipeline;
pub mod validation;
'''

docs['src-tauri/src/application/document/pipeline.rs'] = '''use crate::domain::document::model::DocumentNode;

pub trait Renderer {
    /// Takes a JSON DocumentNode and returns an intermediate string (e.g. HTML or Markdown)
    fn render(&self, doc: &DocumentNode) -> Result<String, String>;
}

/// The orchestrator for converting a JSON AST into a final format.
pub struct RendererPipeline {
    renderers: Vec<Box<dyn Renderer>>,
}

impl RendererPipeline {
    pub fn new() -> Self {
        Self {
            renderers: Vec::new(),
        }
    }

    pub fn add_renderer(&mut self, renderer: Box<dyn Renderer>) {
        self.renderers.push(renderer);
    }

    pub fn execute(&self, doc: &DocumentNode) -> Result<String, String> {
        // In a real pipeline, the output of one renderer might be the input to another,
        // or a specific renderer might handle the whole AST conversion to HTML.
        // For architectural scaffolding, we mock the pipeline execution.
        let mut final_output = String::new();
        for renderer in &self.renderers {
            final_output = renderer.render(doc)?;
        }
        Ok(final_output)
    }
}

pub struct HtmlRenderer;
impl Renderer for HtmlRenderer {
    fn render(&self, doc: &DocumentNode) -> Result<String, String> {
        // Mock AST to HTML conversion
        if doc.r#type == "doc" {
            return Ok("<div class='neocards-doc'>Rendered Document</div>".to_string());
        }
        Ok(String::new())
    }
}
'''

docs['src-tauri/src/application/document/validation.rs'] = '''use crate::domain::document::model::DocumentNode;

pub struct ValidationEngine;

impl ValidationEngine {
    pub fn validate_document(doc: &DocumentNode) -> Result<(), String> {
        if doc.r#type != "doc" {
            return Err("Invalid root node: must be 'doc'".to_string());
        }
        Self::validate_node_recursive(doc)?;
        Ok(())
    }

    fn validate_node_recursive(node: &DocumentNode) -> Result<(), String> {
        // Mock validation: check for unsupported node types or broken media references
        if node.r#type == "unknown_plugin_node" {
            return Err("Unsupported node type detected".to_string());
        }

        if let Some(children) = &node.content {
            for child in children {
                Self::validate_node_recursive(child)?;
            }
        }
        Ok(())
    }
}
'''

for filepath, content in docs.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Document Engine Scaffolding complete.")

