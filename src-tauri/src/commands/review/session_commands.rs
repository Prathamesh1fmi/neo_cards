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
    // MOCK: Fetch next card from QueueManager, render templates, return HTML
    Ok(None)
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

    // 1. Fetch current card
    // let card = fetch_card(&tx, &req.card_id);
    
    // 2. Scheduler Calculation
    let scheduler = FsrsScheduler::new();
    let result = scheduler.calculate_next_review(
        &req.card_id, 
        CardState::Review, 
        req.rating, 
        10, 
        2.5, 
        1, 
        0
    )?;

    // 3. Update Card in DB
    // update_card(&tx, result);

    // 4. Insert RevLog
    // insert_revlog(&tx, req, result);

    tx.commit().map_err(|e| e.to_string())?;
    Ok(())
}