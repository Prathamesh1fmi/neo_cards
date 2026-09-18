use tauri::State;
use uuid::Uuid;
use chrono::Utc;
use crate::db::connection::DbState;
use crate::domain::deck::{Deck, DeckTree};
use crate::infrastructure::deck_repository;

#[tauri::command]
pub fn create_deck(name: String, parent_id: Option<String>, state: State<DbState>) -> Result<Deck, String> {
    let conn = state.conn.lock().unwrap();
    let deck = Deck {
        id: Uuid::new_v4().to_string(),
        parent_id,
        name,
        created_at: Utc::now().timestamp(),
    };
    deck_repository::create_deck(&conn, &deck).map_err(|e| e.to_string())?;
    Ok(deck)
}

#[tauri::command]
pub fn get_deck_tree(state: State<DbState>) -> Result<Vec<DeckTree>, String> {
    let conn = state.conn.lock().unwrap();
    deck_repository::get_deck_tree(&conn).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn delete_deck(id: String, state: State<DbState>) -> Result<(), String> {
    let conn = state.conn.lock().unwrap();
    deck_repository::delete_deck(&conn, &id).map_err(|e| e.to_string())
}