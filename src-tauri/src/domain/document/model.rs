use serde::{Serialize, Deserialize};
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