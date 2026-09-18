use serde::{Serialize, Deserialize};

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