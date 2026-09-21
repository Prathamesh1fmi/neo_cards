use tauri::State;
use crate::db::connection::DbState;
use crate::application::review::scheduler::{Rating, FsrsScheduler, SchedulerService, CardState};
use crate::domain::card::Card;
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct ReviewCardDto {
    pub card: Card,
    pub front_html: String,
    pub back_html: String,
}

#[tauri::command]
pub fn get_next_card(deck_id: String, state: State<DbState>) -> Result<Option<ReviewCardDto>, String> {
    let conn = state.conn.lock().unwrap();
    let now = chrono::Utc::now().timestamp();
    
    let mut stmt = conn.prepare("
        SELECT c.id, c.note_id, c.due_date, c.interval, c.ease_factor, c.reps, c.lapses, c.state, n.content 
        FROM cards c
        JOIN notes n ON c.note_id = n.id
        WHERE n.deck_id = ?1 AND c.due_date <= ?2
        ORDER BY c.due_date ASC
        LIMIT 1
    ").map_err(|e| e.to_string())?;
    
    let card_res = stmt.query_row(rusqlite::params![deck_id, now], |row| {
        let content: String = row.get(8)?;
        Ok((
            Card {
                id: row.get(0)?,
                note_id: row.get(1)?,
                due_date: row.get(2)?,
                interval: row.get(3)?,
                ease_factor: row.get(4)?,
                reps: row.get(5)?,
                lapses: row.get(6)?,
                state: row.get(7)?,
            },
            content
        ))
    });

    if let Ok((card, content)) = card_res {
        let parsed: serde_json::Value = serde_json::from_str(&content).unwrap_or(serde_json::json!({}));
        let fields = parsed.get("fields").and_then(|f| f.as_array()).cloned().unwrap_or_default();
        
        let front = if fields.len() > 0 { fields[0].as_str().unwrap_or("").to_string() } else { "Empty".to_string() };
        let back = if fields.len() > 1 { fields[1].as_str().unwrap_or("").to_string() } else { "Empty".to_string() };

        Ok(Some(ReviewCardDto {
            card,
            front_html: format!("<div class='text-2xl text-center font-medium'>{}</div>", front),
            back_html: format!("<div class='text-2xl text-center text-primary mb-4'>{}</div><hr class='border-border my-4'/>", back),
        }))
    } else {
        Ok(None)
    }
}

#[derive(Deserialize)]
pub struct SubmitReviewRequest {
    pub card_id: String,
    pub rating: Rating,
    pub time_taken_ms: i32,
}

#[tauri::command]
pub fn submit_review(req: SubmitReviewRequest, state: State<DbState>) -> Result<(), String> {
    let mut conn = state.conn.lock().unwrap();
    let tx = conn.transaction().map_err(|e| e.to_string())?;

    let card: Card = tx.query_row(
        "SELECT id, note_id, due_date, interval, ease_factor, reps, lapses, state FROM cards WHERE id = ?1",
        rusqlite::params![req.card_id],
        |row| Ok(Card {
            id: row.get(0)?,
            note_id: row.get(1)?,
            due_date: row.get(2)?,
            interval: row.get(3)?,
            ease_factor: row.get(4)?,
            reps: row.get(5)?,
            lapses: row.get(6)?,
            state: row.get(7)?,
        })
    ).map_err(|e| e.to_string())?;
    
    let scheduler = FsrsScheduler::new();
    let current_state = match card.state {
        0 => CardState::New,
        1 => CardState::Learning,
        2 => CardState::Review,
        _ => CardState::Relearning,
    };
    
    let result = scheduler.calculate_next_review(
        &req.card_id, 
        current_state, 
        req.rating, 
        card.interval, 
        card.ease_factor, 
        card.reps, 
        card.lapses
    )?;

    let new_state = match result.new_state {
        CardState::New => 0,
        CardState::Learning => 1,
        CardState::Review => 2,
        CardState::Relearning => 3,
    };

    tx.execute(
        "UPDATE cards SET due_date = ?1, interval = ?2, ease_factor = ?3, reps = ?4, lapses = ?5, state = ?6 WHERE id = ?7",
        rusqlite::params![result.next_due, result.new_interval, result.new_ease, result.reps, result.lapses, new_state, req.card_id]
    ).map_err(|e| e.to_string())?;

    tx.execute(
        "INSERT INTO revlog (id, card_id, graded, time_taken_ms, created_at) VALUES (?1, ?2, ?3, ?4, ?5)",
        rusqlite::params![uuid::Uuid::new_v4().to_string(), req.card_id, req.rating as i32, req.time_taken_ms, chrono::Utc::now().timestamp()]
    ).map_err(|e| e.to_string())?;

    tx.commit().map_err(|e| e.to_string())?;
    Ok(())
}