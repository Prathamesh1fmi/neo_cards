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
    
    for deck in &decks {
        map.insert(deck.id.clone(), DeckTree {
            deck: deck.clone(),
            children: Vec::new(),
        });
    }

    let mut children_map: HashMap<String, Vec<String>> = HashMap::new();
    let mut root_ids = Vec::new();
    
    for deck in &decks {
        if let Some(parent_id) = &deck.parent_id {
            children_map.entry(parent_id.clone()).or_default().push(deck.id.clone());
        } else {
            root_ids.push(deck.id.clone());
        }
    }
    
    fn build_node(id: &str, map: &HashMap<String, DeckTree>, children_map: &HashMap<String, Vec<String>>) -> DeckTree {
        let mut node = map.get(id).unwrap().clone();
        if let Some(child_ids) = children_map.get(id) {
            for child_id in child_ids {
                node.children.push(build_node(child_id, map, children_map));
            }
        }
        node
    }
    
    let mut roots = Vec::new();
    for root_id in root_ids {
        roots.push(build_node(&root_id, &map, &children_map));
    }

    Ok(roots)
}

pub fn delete_deck(conn: &Connection, id: &str) -> Result<(), rusqlite::Error> {
    conn.execute("DELETE FROM decks WHERE id = ?1", params![id])?;
    Ok(())
}