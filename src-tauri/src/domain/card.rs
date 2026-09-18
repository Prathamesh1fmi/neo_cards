use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Card {
    pub id: String,
    pub note_id: String,
    pub due_date: i64,
    pub interval: i32,
    pub ease_factor: f64,
    pub reps: i32,
    pub lapses: i32,
    pub state: i32, // 0=New, 1=Learning, 2=Review, 3=Suspended
}