use rusqlite::{params, Connection, Transaction};
use crate::domain::card::Card;

pub fn save_card_tx(tx: &Transaction, card: &Card) -> Result<(), rusqlite::Error> {
    tx.execute(
        "INSERT OR REPLACE INTO cards (id, note_id, due_date, interval, ease_factor, reps, lapses, state) 
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
        params![card.id, card.note_id, card.due_date, card.interval, card.ease_factor, card.reps, card.lapses, card.state],
    )?;
    Ok(())
}

pub fn delete_cards_by_note_tx(tx: &Transaction, note_id: &str) -> Result<(), rusqlite::Error> {
    tx.execute("DELETE FROM cards WHERE note_id = ?1", params![note_id])?;
    Ok(())
}