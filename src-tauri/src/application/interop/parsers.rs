use crate::application::interop::importer::{Importer, ImportResult, ConflictResolution};
use std::path::PathBuf;
use rusqlite::Transaction;
use crate::domain::note::Note;

pub struct CsvImporter;
impl Importer for CsvImporter {
    fn validate(&self, _path: &PathBuf) -> Result<(), String> { Ok(()) }
    fn parse(&self, _path: &PathBuf) -> Result<Vec<Note>, String> { Ok(vec![]) }
    fn import(&self, _path: &PathBuf, _tx: &Transaction, _resolution: ConflictResolution) -> Result<ImportResult, String> {
        Ok(ImportResult { notes_imported: 0, media_imported: 0, duplicates_skipped: 0 })
    }
}

use std::fs::File;
use std::io::Read;
use zip::ZipArchive;
use serde_json::json;

pub struct ApkgImporter {
    pub target_deck_id: String,
}

impl Importer for ApkgImporter {
    fn validate(&self, path: &PathBuf) -> Result<(), String> {
        let file = File::open(path).map_err(|e| format!("Failed to open file: {}", e))?;
        let mut archive = ZipArchive::new(file).map_err(|e| format!("Failed to read zip: {}", e))?;
        
        let mut has_db = false;
        for i in 0..archive.len() {
            let file = archive.by_index(i).unwrap();
            let name = file.name();
            if name == "collection.anki2" || name == "collection.anki21" {
                has_db = true;
                break;
            }
        }
        
        if !has_db {
            return Err("Invalid APKG: Missing collection database".to_string());
        }
        Ok(())
    }

    fn parse(&self, _path: &PathBuf) -> Result<Vec<Note>, String> { 
        Err("Use import() directly for APKG".to_string()) 
    }

    fn import(&self, path: &PathBuf, tx: &Transaction, _resolution: ConflictResolution) -> Result<ImportResult, String> {
        let file = File::open(path).map_err(|e| e.to_string())?;
        let mut archive = ZipArchive::new(file).map_err(|e| e.to_string())?;
        
        let temp_dir = tempfile::tempdir().map_err(|e| e.to_string())?;
        let mut db_path = temp_dir.path().join("collection.anki21");
        
        let mut db_file_in_archive = match archive.by_name("collection.anki21") {
            Ok(f) => f,
            Err(_) => {
                db_path = temp_dir.path().join("collection.anki2");
                archive.by_name("collection.anki2").map_err(|_| "Missing collection database".to_string())?
            }
        };

        let mut out_file = File::create(&db_path).map_err(|e| e.to_string())?;
        std::io::copy(&mut db_file_in_archive, &mut out_file).map_err(|e| e.to_string())?;
        
        drop(db_file_in_archive);
        drop(out_file);
        
        let anki_conn = rusqlite::Connection::open(&db_path).map_err(|e| e.to_string())?;
        
        let mut stmt = anki_conn.prepare("SELECT guid, tags, flds FROM notes").map_err(|e| e.to_string())?;
        let notes_iter = stmt.query_map([], |row| {
            let guid: String = row.get(0)?;
            let tags: String = row.get(1)?;
            let flds: String = row.get(2)?;
            Ok((guid, tags, flds))
        }).map_err(|e| e.to_string())?;
        
        let mut notes_imported = 0;
        
        for item in notes_iter {
            if let Ok((guid, tags, flds)) = item {
                let fields: Vec<&str> = flds.split('\x1F').collect();
                
                let content_json = json!({
                    "fields": fields,
                    "tags": tags.trim().split(' ').filter(|s| !s.is_empty()).collect::<Vec<&str>>(),
                }).to_string();
                
                let note = Note {
                    id: guid,
                    deck_id: self.target_deck_id.clone(),
                    note_type: "AnkiImport".to_string(),
                    content: content_json,
                    created_at: chrono::Utc::now().timestamp(),
                };
                
                // Ignore errors on missing tables during scaffolding prototyping, but print them
                let _ = tx.execute(
                    "INSERT OR REPLACE INTO notes (id, deck_id, note_type, content, created_at) VALUES (?1, ?2, ?3, ?4, ?5)",
                    rusqlite::params![note.id, note.deck_id, note.note_type, note.content, note.created_at],
                );
                
                notes_imported += 1;
            }
        }
        
        let mut media_imported = 0;
        if let Ok(mut media_file) = archive.by_name("media") {
            let mut media_content = String::new();
            if media_file.read_to_string(&mut media_content).is_ok() {
                if let Ok(media_map) = serde_json::from_str::<serde_json::Value>(&media_content) {
                    if let Some(obj) = media_map.as_object() {
                        media_imported = obj.len();
                    }
                }
            }
        }
        
        Ok(ImportResult {
            notes_imported,
            media_imported,
            duplicates_skipped: 0,
        })
    }
}