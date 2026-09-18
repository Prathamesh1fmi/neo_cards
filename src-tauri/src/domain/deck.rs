use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Deck {
    pub id: String,
    pub parent_id: Option<String>,
    pub name: String,
    pub created_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeckTree {
    pub deck: Deck,
    pub children: Vec<DeckTree>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeckSettings {
    pub deck_id: String,
    pub new_cards_per_day: i32,
    pub reviews_per_day: i32,
}