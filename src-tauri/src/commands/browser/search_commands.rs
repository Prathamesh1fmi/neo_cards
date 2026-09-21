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
pub struct CardBrowserDto {
    pub card_id: String,
    pub note_id: String,
    pub front: String,
    pub deck: String,
    pub due: String,
    pub state: String,
}

#[tauri::command]
pub fn search_cards(query: String, state: State<DbState>) -> Result<Vec<CardBrowserDto>, String> {
    let conn = state.conn.lock().unwrap();
    
    let sql = "
        SELECT c.id, n.id, n.content, d.name, c.due_date, c.state
        FROM cards c
        JOIN notes n ON c.note_id = n.id
        JOIN decks d ON n.deck_id = d.id
        WHERE n.content LIKE ?1
        ORDER BY c.due_date ASC
        LIMIT 500
    ";
    
    let search_term = format!("%{}%", query);
    let mut stmt = conn.prepare(sql).map_err(|e| e.to_string())?;
    
    let iter = stmt.query_map(rusqlite::params![search_term], |row| {
        let content: String = row.get(2)?;
        let due_date: i64 = row.get(4)?;
        let state: i32 = row.get(5)?;
        
        Ok((
            row.get::<_, String>(0)?,
            row.get::<_, String>(1)?,
            content,
            row.get::<_, String>(3)?,
            due_date,
            state
        ))
    }).map_err(|e| e.to_string())?;

    let mut results = Vec::new();
    for item in iter {
        if let Ok((card_id, note_id, content, deck, due_date, state)) = item {
            let parsed: serde_json::Value = serde_json::from_str(&content).unwrap_or(serde_json::json!({}));
            let fields = parsed.get("fields").and_then(|f| f.as_array()).cloned().unwrap_or_default();
            let front = if fields.len() > 0 { fields[0].as_str().unwrap_or("").to_string() } else { "Empty".to_string() };
            
            // Format due date to a readable string (e.g. YYYY-MM-DD or days relative)
            // For now, we'll just use a simple date format if it's a timestamp
            let due = if due_date > 1000000 {
                chrono::DateTime::from_timestamp(due_date, 0)
                    .map(|dt| dt.format("%Y-%m-%d").to_string())
                    .unwrap_or_else(|| due_date.to_string())
            } else {
                due_date.to_string()
            };

            let state_str = match state {
                0 => "New",
                1 => "Learning",
                2 => "Review",
                _ => "Suspended",
            }.to_string();

            results.push(CardBrowserDto {
                card_id,
                note_id,
                front,
                deck,
                due,
                state: state_str,
            });
        }
    }
    
    Ok(results)
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