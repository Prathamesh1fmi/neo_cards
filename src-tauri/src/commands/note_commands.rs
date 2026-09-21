use tauri::State;
use uuid::Uuid;
use chrono::Utc;
use crate::db::connection::DbState;
use serde_json::json;

#[tauri::command]
pub fn add_note(deck_id: String, front_html: String, back_html: String, state: State<DbState>) -> Result<(), String> {
    let mut conn = state.conn.lock().unwrap();
    let tx = conn.transaction().map_err(|e| e.to_string())?;

    let note_id = Uuid::new_v4().to_string();
    let created_at = Utc::now().timestamp();

    // Replicate Anki note structure: 
    // Usually Anki notes have multiple fields. We'll store it as a JSON payload for flexibility.
    let content = json!({
        "fields": [front_html, back_html]
    }).to_string();

    tx.execute(
        "INSERT INTO notes (id, deck_id, note_type, content, created_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        rusqlite::params![note_id, deck_id, "Basic", content, created_at]
    ).map_err(|e| e.to_string())?;

    // Create a corresponding Card (State 0 = New)
    let card_id = Uuid::new_v4().to_string();
    tx.execute(
        "INSERT INTO cards (id, note_id, due_date, interval, ease_factor, reps, lapses, state) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
        rusqlite::params![card_id, note_id, created_at, 0, 2.5, 0, 0, 0] // 0 = New state
    ).map_err(|e| e.to_string())?;

    tx.commit().map_err(|e| e.to_string())?;

    Ok(())
}
