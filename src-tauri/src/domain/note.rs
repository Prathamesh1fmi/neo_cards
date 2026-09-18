use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Note {
    pub id: String,
    pub deck_id: String,
    pub note_type: String, // e.g., "Basic", "Cloze"
    pub content: String,   // JSON payload of fields (Front/Back)
    pub created_at: i64,
}