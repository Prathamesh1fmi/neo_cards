use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AppEvent {
    NoteCreated { note_id: String },
    NoteUpdated { note_id: String },
    CardReviewed { card_id: String, rating: i32 },
    DeckCreated { deck_id: String },
    PluginLoaded { plugin_id: String },
}

type EventHandler = Box<dyn Fn(&AppEvent) + Send + Sync>;

pub struct EventBus {
    listeners: HashMap<String, Vec<EventHandler>>,
}

impl EventBus {
    pub fn new() -> Self {
        Self { listeners: HashMap::new() }
    }

    pub fn publish(&self, event: AppEvent) {
        // MOCK: Dispatches event to all registered plugin listeners.
    }
}