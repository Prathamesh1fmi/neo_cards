use crate::domain::card::Card;
use crate::application::review::scheduler::{Rating, SchedulerService};
use rusqlite::Connection;

pub struct QueueManager {
    // Queues
    pub new_queue: Vec<Card>,
    pub learning_queue: Vec<Card>,
    pub review_queue: Vec<Card>,
}

impl QueueManager {
    pub fn build(conn: &Connection, deck_id: &str) -> Result<Self, String> {
        // MOCK: In production, query cards WHERE deck_id = ? AND due_date <= NOW()
        Ok(Self {
            new_queue: Vec::new(),
            learning_queue: Vec::new(),
            review_queue: Vec::new(),
        })
    }

    pub fn get_next_card(&mut self) -> Option<Card> {
        // Prioritize Learning > Review > New
        if !self.learning_queue.is_empty() {
            return Some(self.learning_queue.remove(0));
        }
        if !self.review_queue.is_empty() {
            return Some(self.review_queue.remove(0));
        }
        if !self.new_queue.is_empty() {
            return Some(self.new_queue.remove(0));
        }
        None
    }
}