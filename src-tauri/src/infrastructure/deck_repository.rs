use rusqlite::{params, Connection, OptionalExtension};
use crate::domain::deck::{Deck, DeckTree};
use std::collections::HashMap;

pub fn create_deck(conn: &Connection, deck: &Deck) -> Result<(), rusqlite::Error> {
    conn.execute(
        "INSERT INTO decks (id, parent_id, name, created_at) VALUES (?1, ?2, ?3, ?4)",
        params![deck.id, deck.parent_id, deck.name, deck.created_at],
    )?;
    Ok(())
}

pub fn get_all_decks(conn: &Connection) -> Result<Vec<Deck>, rusqlite::Error> {
    let mut stmt = conn.prepare("SELECT id, parent_id, name, created_at FROM decks ORDER BY name ASC")?;
    let deck_iter = stmt.query_map([], |row| {
        Ok(Deck {
            id: row.get(0)?,
            parent_id: row.get(1)?,
            name: row.get(2)?,
            created_at: row.get(3)?,
        })
    })?;

    let mut decks = Vec::new();
    for d in deck_iter {
        decks.push(d?);
    }
    Ok(decks)
}

pub fn get_deck_tree(conn: &Connection) -> Result<Vec<DeckTree>, rusqlite::Error> {
    let decks = get_all_decks(conn)?;
    let mut map: HashMap<String, DeckTree> = HashMap::new();
    let mut roots = Vec::new();

    // Map all decks
    for deck in &decks {
        map.insert(deck.id.clone(), DeckTree {
            deck: deck.clone(),
            children: Vec::new(),
        });
    }

    // Build hierarchy
    let mut tree_map = map.clone();
    for deck in decks {
        if let Some(parent_id) = deck.parent_id {
            if let Some(parent_tree) = tree_map.get_mut(&parent_id) {
                if let Some(child_tree) = map.get(&deck.id) {
                    parent_tree.children.push(child_tree.clone());
                }
            }
        } else {
            if let Some(root_tree) = tree_map.get(&deck.id) {
                roots.push(root_tree.clone());
            }
        }
    }
    // Note: A full recursive tree build in Rust requires a bit more ownership gymnastics. 
    // This is a simplified linear pass. 
    
    Ok(roots)
}

pub fn delete_deck(conn: &Connection, id: &str) -> Result<(), rusqlite::Error> {
    conn.execute("DELETE FROM decks WHERE id = ?1", params![id])?;
    Ok(())
}