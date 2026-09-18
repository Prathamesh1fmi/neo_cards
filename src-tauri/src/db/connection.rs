use rusqlite::Connection;
use std::sync::Mutex;
use std::path::PathBuf;

pub struct DbState {
    pub conn: Mutex<Connection>,
}

pub fn establish_connection(db_path: PathBuf) -> Result<Connection, rusqlite::Error> {
    let conn = Connection::open(db_path)?;
    // Enable performance & integrity features
    conn.execute_batch("
        PRAGMA journal_mode = WAL;
        PRAGMA synchronous = NORMAL;
        PRAGMA foreign_keys = ON;
        PRAGMA cache_size = -64000;
    ")?;
    Ok(conn)
}