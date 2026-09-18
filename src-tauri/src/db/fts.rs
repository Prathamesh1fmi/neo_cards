use rusqlite::{Connection, params};

/// Initializes the FTS5 virtual tables for the document engine.
/// We strictly index plain text extracted from the JSON AST, never HTML.
pub fn setup_fts_tables(conn: &Connection) -> Result<(), rusqlite::Error> {
    conn.execute_batch(
        "
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
            note_id UNINDEXED,
            deck_id UNINDEXED,
            content,
            tags,
            tokenize = 'porter unicode61'
        );

        -- Trigger to automatically push text into FTS when a note is inserted.
        -- In a robust system, the JSON->Text extraction should happen in Rust before INSERT,
        -- but SQLite JSON functions can be used for basic extraction.
        -- We assume Rust extracts the `plain_text` and inserts it alongside the JSON, 
        -- or Rust directly inserts into `notes_fts` within the save transaction.
        "
    )?;
    Ok(())
}

/// Helper function to traverse the Tiptap JSON AST and extract pure text for search
pub fn extract_text_from_json_ast(json_str: &str) -> String {
    // MOCK: In production, parse JSON and recursively extract the 'text' fields 
    // from paragraphs, headings, blockquotes, ignoring marks and structure.
    "extracted plain text string".to_string()
}