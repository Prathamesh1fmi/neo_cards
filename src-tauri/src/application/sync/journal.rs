use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SyncOperation {
    Insert,
    Update,
    Delete,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JournalRecord {
    pub id: String,
    pub entity: String, // "Note", "Card", "Deck"
    pub entity_id: String,
    pub operation: SyncOperation,
    pub payload_hash: String,
    pub device_id: String,
    pub timestamp: i64,
    pub synced: bool,
}

/// The durable queue tracking all local mutations.
/// Transactions write to their tables AND this journal atomically.
pub trait SyncJournal {
    fn append(&self, record: &JournalRecord) -> Result<(), String>;
    fn get_unsynced(&self) -> Result<Vec<JournalRecord>, String>;
    fn mark_synced(&self, ids: &[String]) -> Result<(), String>;
}