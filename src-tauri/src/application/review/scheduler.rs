use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Rating {
    Again = 1,
    Hard = 2,
    Good = 3,
    Easy = 4,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CardState {
    New = 0,
    Learning = 1,
    Review = 2,
    Relearning = 3,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedulingInfo {
    pub card_id: String,
    pub next_due: i64,
    pub new_interval: i32,
    pub new_ease: f64,
    pub new_state: CardState,
    pub reps: i32,
    pub lapses: i32,
}

/// Abstract Scheduler Service. NeoCards depends on this trait, NOT FSRS directly.
pub trait SchedulerService {
    fn calculate_next_review(
        &self, 
        card_id: &str, 
        current_state: CardState, 
        rating: Rating, 
        current_interval: i32, 
        current_ease: f64, 
        reps: i32, 
        lapses: i32
    ) -> Result<SchedulingInfo, String>;
}

/// FSRS Implementation of the Scheduler Service
pub struct FsrsScheduler {
    // Internally, this wraps the `fsrs::FSRS` struct
    // For scaffolding, we mock the mathematical calculations to prove the architecture
}

impl FsrsScheduler {
    pub fn new() -> Self {
        Self {}
    }
}

impl SchedulerService for FsrsScheduler {
    fn calculate_next_review(
        &self, 
        card_id: &str, 
        current_state: CardState, 
        rating: Rating, 
        current_interval: i32, 
        current_ease: f64, 
        reps: i32, 
        lapses: i32
    ) -> Result<SchedulingInfo, String> {
        // MOCK FSRS CALCULATION FOR ARCHITECTURE VALIDATION
        let mut new_reps = reps + 1;
        let mut new_lapses = lapses;
        let mut next_due = chrono::Utc::now().timestamp();
        let mut new_state = CardState::Review;
        
        let new_interval = match rating {
            Rating::Again => {
                new_lapses += 1;
                new_state = if current_state == CardState::New { CardState::Learning } else { CardState::Relearning };
                0
            },
            Rating::Hard => (current_interval as f64 * 1.2) as i32,
            Rating::Good => (current_interval as f64 * 2.5) as i32,
            Rating::Easy => (current_interval as f64 * 3.1) as i32,
        };

        if new_interval > 0 {
            next_due += (new_interval as i64) * 86400; // days to seconds
        }

        Ok(SchedulingInfo {
            card_id: card_id.to_string(),
            next_due,
            new_interval: std::cmp::max(new_interval, 1),
            new_ease: current_ease, // FSRS calculates stability/difficulty internally
            new_state,
            reps: new_reps,
            lapses: new_lapses,
        })
    }
}