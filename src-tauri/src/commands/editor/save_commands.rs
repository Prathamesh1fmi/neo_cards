use tauri::State;
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