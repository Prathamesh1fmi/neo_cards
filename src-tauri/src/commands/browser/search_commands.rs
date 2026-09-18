use tauri::State;
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