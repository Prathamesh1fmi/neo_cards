use tauri::State;
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