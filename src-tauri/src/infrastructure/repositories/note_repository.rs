use rusqlite::{params, Connection, Transaction};
use crate::domain::note::Note;

pub fn save_note_tx(tx: &Transaction, note: &Note) -> Result<(), rusqlite::Error> {
    tx.execute(
        "INSERT OR REPLACE INTO notes (id, deck_id, note_type, content, created_at) 
         VALUES (?1, ?2, ?3, ?4, ?5)",
        params![note.id, note.deck_id, note.note_type, note.content, note.created_at],
    )?;
    
    // Future FTS extraction logic would go here
    Ok(())
}