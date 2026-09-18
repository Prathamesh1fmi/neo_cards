use rusqlite::Connection;

pub fn run_migrations(conn: &Connection) -> Result<(), rusqlite::Error> {
    conn.execute_batch(
        "
        CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY);
        INSERT OR IGNORE INTO schema_version (version) VALUES (1);

        CREATE TABLE IF NOT EXISTS decks (
            id TEXT PRIMARY KEY,
            parent_id TEXT,
            name TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(parent_id) REFERENCES decks(id) ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_decks_parent_name ON decks(parent_id, name);

        CREATE TABLE IF NOT EXISTS deck_settings (
            deck_id TEXT PRIMARY KEY,
            new_cards_per_day INTEGER NOT NULL DEFAULT 20,
            reviews_per_day INTEGER NOT NULL DEFAULT 200,
            FOREIGN KEY(deck_id) REFERENCES decks(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            deck_id TEXT NOT NULL,
            note_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(deck_id) REFERENCES decks(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS tags (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS note_tags (
            note_id TEXT NOT NULL,
            tag_id TEXT NOT NULL,
            PRIMARY KEY(note_id, tag_id),
            FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS cards (
            id TEXT PRIMARY KEY,
            note_id TEXT NOT NULL,
            due_date INTEGER NOT NULL,
            interval INTEGER NOT NULL,
            ease_factor REAL NOT NULL,
            reps INTEGER NOT NULL,
            lapses INTEGER NOT NULL,
            state INTEGER NOT NULL,
            FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_cards_due ON cards(due_date);

        CREATE TABLE IF NOT EXISTS revlog (
            id TEXT PRIMARY KEY,
            card_id TEXT NOT NULL,
            graded INTEGER NOT NULL,
            time_taken_ms INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS media (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        "
    )?;
    Ok(())
}