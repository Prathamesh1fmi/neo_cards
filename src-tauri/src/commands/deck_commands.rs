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

use crate::domain::deck::DeckSettings;

#[tauri::command]
pub fn get_deck_settings(deck_id: String, state: State<DbState>) -> Result<DeckSettings, String> {
    let conn = state.conn.lock().unwrap();
    let mut stmt = conn.prepare("SELECT new_cards_per_day, reviews_per_day FROM deck_settings WHERE deck_id = ?1").map_err(|e| e.to_string())?;
    let mut rows = stmt.query(rusqlite::params![deck_id]).map_err(|e| e.to_string())?;
    
    if let Some(row) = rows.next().map_err(|e| e.to_string())? {
        Ok(DeckSettings {
            deck_id,
            new_cards_per_day: row.get(0).map_err(|e| e.to_string())?,
            reviews_per_day: row.get(1).map_err(|e| e.to_string())?,
        })
    } else {
        // Return default settings if none exist
        Ok(DeckSettings {
            deck_id,
            new_cards_per_day: 20,
            reviews_per_day: 200,
        })
    }
}

#[tauri::command]
pub fn update_deck_settings(settings: DeckSettings, state: State<DbState>) -> Result<(), String> {
    let conn = state.conn.lock().unwrap();
    conn.execute(
        "INSERT OR REPLACE INTO deck_settings (deck_id, new_cards_per_day, reviews_per_day) VALUES (?1, ?2, ?3)",
        rusqlite::params![settings.deck_id, settings.new_cards_per_day, settings.reviews_per_day]
    ).map_err(|e| e.to_string())?;
    Ok(())
}