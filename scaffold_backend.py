import os
from pathlib import Path

base = Path('.')

dirs = [
    'tools',
    'src-tauri/src/db',
    'src-tauri/src/domain',
    'src-tauri/src/infrastructure',
    'src-tauri/src/commands'
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# PowerShell Scripts
scripts['setup.ps1'] = '''Continue = "Stop"

 = "\\tools"
 = "\\node"
 = "v20.12.0"
 = "node--win-x64.zip"
 = "https://nodejs.org/dist//"

if (!(Test-Path )) { New-Item -ItemType Directory -Force -Path  | Out-Null }

Write-Host "Verifying Node.js..."
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "Global Node.js detected." -ForegroundColor Green
} elseif (Test-Path "\\node.exe") {
    Write-Host "Portable Node.js detected." -ForegroundColor Green
} else {
    Write-Host "Node.js not found. Downloading portable version ()..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri  -OutFile "\\"
    Expand-Archive -Path "\\" -DestinationPath  -Force
    Rename-Item -Path "\\node--win-x64" -NewName "node"
    Remove-Item -Path "\\"
    Write-Host "Portable Node.js installed." -ForegroundColor Green
}

Write-Host "Verifying Rust..."
if (Get-Command cargo -ErrorAction SilentlyContinue) {
    Write-Host "Global Rust/Cargo detected." -ForegroundColor Green
} else {
    Write-Host "WARNING: Cargo not found in PATH." -ForegroundColor Red
    Write-Host "A fully portable Rust toolchain is not feasible on Windows due to heavy dependencies on the MSVC C++ Build Tools." -ForegroundColor Yellow
    Write-Host "Please install Rust globally via https://rustup.rs and ensure MSVC C++ build tools are installed." -ForegroundColor Yellow
}

Write-Host "Setup complete!"
'''

scripts['dev.ps1'] = ''' = "\\tools\\node"
if (Test-Path "\\node.exe") {
    C:/Users/PrathameshK/.gemini/antigravity/bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Users\PrathameshK\AppData\Local\agy\bin;C:\Users\PrathameshK\scoop\shims;C:\Users\PrathameshK\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\Scripts\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Launcher\;C:\Users\PrathameshK\AppData\Local\Microsoft\WindowsApps;C:\Users\PrathameshK\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\PrathameshK\.local\bin;C:\Users\PrathameshK\AppData\Local\Programs\Git\cmd;C:\Users\PrathameshK\AppData\Local\Microsoft\WinGet\Packages\eza-community.eza_Microsoft.Winget.Source_8wekyb3d8bbwe;C:\Users\PrathameshK\AppData\Local\Programs\cursor\resources\app\bin = ";" + C:/Users/PrathameshK/.gemini/antigravity/bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Users\PrathameshK\AppData\Local\agy\bin;C:\Users\PrathameshK\scoop\shims;C:\Users\PrathameshK\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\Scripts\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Launcher\;C:\Users\PrathameshK\AppData\Local\Microsoft\WindowsApps;C:\Users\PrathameshK\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\PrathameshK\.local\bin;C:\Users\PrathameshK\AppData\Local\Programs\Git\cmd;C:\Users\PrathameshK\AppData\Local\Microsoft\WinGet\Packages\eza-community.eza_Microsoft.Winget.Source_8wekyb3d8bbwe;C:\Users\PrathameshK\AppData\Local\Programs\cursor\resources\app\bin
}
if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Error: npm not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}
if (!(Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "Error: cargo not found. Please install Rust (https://rustup.rs)." -ForegroundColor Red
    exit 1
}
npm run tauri dev
'''

scripts['build.ps1'] = ''' = "\\tools\\node"
if (Test-Path "\\node.exe") {
    C:/Users/PrathameshK/.gemini/antigravity/bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Users\PrathameshK\AppData\Local\agy\bin;C:\Users\PrathameshK\scoop\shims;C:\Users\PrathameshK\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\Scripts\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Launcher\;C:\Users\PrathameshK\AppData\Local\Microsoft\WindowsApps;C:\Users\PrathameshK\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\PrathameshK\.local\bin;C:\Users\PrathameshK\AppData\Local\Programs\Git\cmd;C:\Users\PrathameshK\AppData\Local\Microsoft\WinGet\Packages\eza-community.eza_Microsoft.Winget.Source_8wekyb3d8bbwe;C:\Users\PrathameshK\AppData\Local\Programs\cursor\resources\app\bin = ";" + C:/Users/PrathameshK/.gemini/antigravity/bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Users\PrathameshK\AppData\Local\agy\bin;C:\Users\PrathameshK\scoop\shims;C:\Users\PrathameshK\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\Scripts\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Launcher\;C:\Users\PrathameshK\AppData\Local\Microsoft\WindowsApps;C:\Users\PrathameshK\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\PrathameshK\.local\bin;C:\Users\PrathameshK\AppData\Local\Programs\Git\cmd;C:\Users\PrathameshK\AppData\Local\Microsoft\WinGet\Packages\eza-community.eza_Microsoft.Winget.Source_8wekyb3d8bbwe;C:\Users\PrathameshK\AppData\Local\Programs\cursor\resources\app\bin
}
npm run tauri build
'''

scripts['test.ps1'] = ''' = "\\tools\\node"
if (Test-Path "\\node.exe") {
    C:/Users/PrathameshK/.gemini/antigravity/bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Users\PrathameshK\AppData\Local\agy\bin;C:\Users\PrathameshK\scoop\shims;C:\Users\PrathameshK\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\Scripts\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Launcher\;C:\Users\PrathameshK\AppData\Local\Microsoft\WindowsApps;C:\Users\PrathameshK\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\PrathameshK\.local\bin;C:\Users\PrathameshK\AppData\Local\Programs\Git\cmd;C:\Users\PrathameshK\AppData\Local\Microsoft\WinGet\Packages\eza-community.eza_Microsoft.Winget.Source_8wekyb3d8bbwe;C:\Users\PrathameshK\AppData\Local\Programs\cursor\resources\app\bin = ";" + C:/Users/PrathameshK/.gemini/antigravity/bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Users\PrathameshK\AppData\Local\agy\bin;C:\Users\PrathameshK\scoop\shims;C:\Users\PrathameshK\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\Scripts\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Python314\;C:\Users\PrathameshK\AppData\Local\Programs\Python\Launcher\;C:\Users\PrathameshK\AppData\Local\Microsoft\WindowsApps;C:\Users\PrathameshK\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\PrathameshK\.local\bin;C:\Users\PrathameshK\AppData\Local\Programs\Git\cmd;C:\Users\PrathameshK\AppData\Local\Microsoft\WinGet\Packages\eza-community.eza_Microsoft.Winget.Source_8wekyb3d8bbwe;C:\Users\PrathameshK\AppData\Local\Programs\cursor\resources\app\bin
}
Write-Host "Running Frontend Tests..."
npm run test
Write-Host "Running Backend Tests..."
cd src-tauri
cargo test
'''

# Batch wrapper scripts
scripts['setup.bat'] = '''@echo off
powershell.exe -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
'''
scripts['dev.bat'] = '''@echo off
powershell.exe -ExecutionPolicy Bypass -File "%~dp0dev.ps1"
'''
scripts['build.bat'] = '''@echo off
powershell.exe -ExecutionPolicy Bypass -File "%~dp0build.ps1"
'''
scripts['test.bat'] = '''@echo off
powershell.exe -ExecutionPolicy Bypass -File "%~dp0test.ps1"
'''

# RUST BACKEND CODE
scripts['src-tauri/Cargo.toml'] = '''[package]
name = "neocards"
version = "0.1.0"
description = "A local-first learning platform"
authors = ["NeoCards Team"]
edition = "2021"

[build-dependencies]
tauri-build = { version = "1.5", features = [] }

[dependencies]
tauri = { version = "1.5", features = ["shell-open"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
rusqlite = { version = "0.31.0", features = ["bundled"] }
uuid = { version = "1.8", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }
thiserror = "1.0"

[features]
custom-protocol = ["tauri/custom-protocol"]
'''

scripts['src-tauri/src/domain/mod.rs'] = '''pub mod deck;
pub mod note;
pub mod card;
'''

scripts['src-tauri/src/domain/deck.rs'] = '''use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Deck {
    pub id: String,
    pub name: String,
    pub created_at: i64,
}
'''

scripts['src-tauri/src/domain/note.rs'] = '''use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Note {
    pub id: String,
    pub deck_id: String,
    pub note_type: String, // e.g., "Basic", "Cloze"
    pub content: String,   // JSON payload of fields (Front/Back)
    pub created_at: i64,
}
'''

scripts['src-tauri/src/domain/card.rs'] = '''use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Card {
    pub id: String,
    pub note_id: String,
    pub due_date: i64,
    pub interval: i32,
    pub ease_factor: f64,
    pub reps: i32,
    pub lapses: i32,
    pub state: i32, // 0=New, 1=Learning, 2=Review, 3=Suspended
}
'''

scripts['src-tauri/src/db/mod.rs'] = '''pub mod connection;
pub mod migrations;
'''

scripts['src-tauri/src/db/connection.rs'] = '''use rusqlite::Connection;
use std::sync::Mutex;
use std::path::PathBuf;

pub struct DbState {
    pub conn: Mutex<Connection>,
}

pub fn establish_connection(db_path: PathBuf) -> Result<Connection, rusqlite::Error> {
    Connection::open(db_path)
}
'''

scripts['src-tauri/src/db/migrations.rs'] = '''use rusqlite::Connection;

pub fn run_migrations(conn: &Connection) -> Result<(), rusqlite::Error> {
    conn.execute_batch(
        "
        CREATE TABLE IF NOT EXISTS decks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            deck_id TEXT NOT NULL,
            note_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(deck_id) REFERENCES decks(id) ON DELETE CASCADE
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

        CREATE TABLE IF NOT EXISTS revlog (
            id TEXT PRIMARY KEY,
            card_id TEXT NOT NULL,
            graded INTEGER NOT NULL,
            time_taken_ms INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
        );
        "
    )?;
    Ok(())
}
'''

scripts['src-tauri/src/infrastructure/mod.rs'] = '''pub mod deck_repository;
'''

scripts['src-tauri/src/infrastructure/deck_repository.rs'] = '''use rusqlite::{params, Connection};
use crate::domain::deck::Deck;

pub fn create_deck(conn: &Connection, deck: &Deck) -> Result<(), rusqlite::Error> {
    conn.execute(
        "INSERT INTO decks (id, name, created_at) VALUES (?1, ?2, ?3)",
        params![deck.id, deck.name, deck.created_at],
    )?;
    Ok(())
}

pub fn get_decks(conn: &Connection) -> Result<Vec<Deck>, rusqlite::Error> {
    let mut stmt = conn.prepare("SELECT id, name, created_at FROM decks ORDER BY name ASC")?;
    let deck_iter = stmt.query_map([], |row| {
        Ok(Deck {
            id: row.get(0)?,
            name: row.get(1)?,
            created_at: row.get(2)?,
        })
    })?;

    let mut decks = Vec::new();
    for deck in deck_iter {
        decks.push(deck?);
    }
    Ok(decks)
}
'''

scripts['src-tauri/src/commands/mod.rs'] = '''pub mod deck_commands;
'''

scripts['src-tauri/src/commands/deck_commands.rs'] = '''use tauri::State;
use uuid::Uuid;
use chrono::Utc;
use crate::db::connection::DbState;
use crate::domain::deck::Deck;
use crate::infrastructure::deck_repository;

#[tauri::command]
pub fn create_deck(name: String, state: State<DbState>) -> Result<Deck, String> {
    let conn = state.conn.lock().unwrap();
    
    let deck = Deck {
        id: Uuid::new_v4().to_string(),
        name,
        created_at: Utc::now().timestamp(),
    };

    match deck_repository::create_deck(&conn, &deck) {
        Ok(_) => Ok(deck),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
pub fn get_decks(state: State<DbState>) -> Result<Vec<Deck>, String> {
    let conn = state.conn.lock().unwrap();
    
    match deck_repository::get_decks(&conn) {
        Ok(decks) => Ok(decks),
        Err(e) => Err(e.to_string()),
    }
}
'''

scripts['src-tauri/src/main.rs'] = '''#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod db;
mod commands;
mod domain;
mod infrastructure;

use std::sync::Mutex;
use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let app_dir = app.path_resolver().app_data_dir().unwrap_or_else(|| std::path::PathBuf::from("."));
            std::fs::create_dir_all(&app_dir).unwrap();
            
            let db_path = app_dir.join("neocards.sqlite");
            
            // Initialize connection and run migrations
            let conn = db::connection::establish_connection(db_path).expect("Failed to connect to SQLite");
            db::migrations::run_migrations(&conn).expect("Failed to run migrations");

            // Inject the DbState into Tauri
            app.manage(db::connection::DbState {
                conn: Mutex::new(conn),
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::deck_commands::create_deck,
            commands::deck_commands::get_decks
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Backend scaffolding complete.")
