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
    pub media_dir: std::path::PathBuf,
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
        
        let mut is_anki21 = false;
        for i in 0..archive.len() {
            if archive.by_index(i).map_err(|e| e.to_string())?.name() == "collection.anki21" {
                is_anki21 = true;
                break;
            }
        }
        
        let db_path = temp_dir.path().join(if is_anki21 { "collection.anki21" } else { "collection.anki2" });
        let mut db_file_in_archive = archive.by_name(if is_anki21 { "collection.anki21" } else { "collection.anki2" })
            .map_err(|_| "Missing collection database".to_string())?;

        let mut out_file = File::create(&db_path).map_err(|e| e.to_string())?;
        std::io::copy(&mut db_file_in_archive, &mut out_file).map_err(|e| e.to_string())?;
        
        drop(db_file_in_archive);
        drop(out_file);
        
        let anki_conn = rusqlite::Connection::open(&db_path).map_err(|e| e.to_string())?;
        
        let mut stmt = anki_conn.prepare("SELECT guid, tags, flds, id FROM notes").map_err(|e| e.to_string())?;
        let notes_iter = stmt.query_map([], |row| {
            let guid: String = row.get(0)?;
            let tags: String = row.get(1)?;
            let flds: String = row.get(2)?;
            let nid: i64 = row.get(3)?;
            Ok((guid, tags, flds, nid))
        }).map_err(|e| e.to_string())?;
        
        let mut notes_imported = 0;
        
        for item in notes_iter {
            if let Ok((guid, tags, flds, nid)) = item {
                let fields: Vec<&str> = flds.split('\x1F').collect();
                
                let content_json = json!({
                    "fields": fields,
                    "tags": tags.trim().split(' ').filter(|s| !s.is_empty()).collect::<Vec<&str>>(),
                }).to_string();
                
                let note = Note {
                    id: guid.clone(),
                    deck_id: self.target_deck_id.clone(),
                    note_type: "AnkiImport".to_string(),
                    content: content_json,
                    created_at: chrono::Utc::now().timestamp(),
                };
                
                let _ = tx.execute(
                    "INSERT OR REPLACE INTO notes (id, deck_id, note_type, content, created_at) VALUES (?1, ?2, ?3, ?4, ?5)",
                    rusqlite::params![note.id, note.deck_id, note.note_type, note.content, note.created_at],
                );
                notes_imported += 1;

                // Now import the cards associated with this note
                if let Ok(mut card_stmt) = anki_conn.prepare("SELECT id, due, ivl, factor, reps, lapses, queue FROM cards WHERE nid = ?1") {
                    let _ = card_stmt.query_map(rusqlite::params![nid], |row| {
                        let cid: i64 = row.get(0)?;
                        let due: i64 = row.get(1)?;
                        let ivl: i64 = row.get(2)?;
                        let factor: i64 = row.get(3)?;
                        let reps: i64 = row.get(4)?;
                        let lapses: i64 = row.get(5)?;
                        let queue: i64 = row.get(6)?; // Anki queue: 0=new, 1=learning, 2=review, 3=day learn, -1=suspended
                        Ok((cid, due, ivl, factor, reps, lapses, queue))
                    }).and_then(|cards_iter| {
                        for card_res in cards_iter {
                            if let Ok((cid, due, ivl, factor, reps, lapses, queue)) = card_res {
                                // Anki factors are stored as 2500 for 250% (2.5)
                                let ease_factor = (factor as f64) / 1000.0;
                                let _ = tx.execute(
                                    "INSERT OR REPLACE INTO cards (id, note_id, due_date, interval, ease_factor, reps, lapses, state) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
                                    rusqlite::params![cid.to_string(), note.id, due, ivl, ease_factor, reps, lapses, queue],
                                );
                            }
                        }
                        Ok(())
                    });
                }
            }
        }
        
        let mut media_imported = 0;
        let mut media_content = String::new();
        
        // Read media content and immediately drop the mutable borrow
        if let Ok(mut media_file) = archive.by_name("media") {
            let _ = media_file.read_to_string(&mut media_content);
        }

        if !media_content.is_empty() {
            if let Ok(media_map) = serde_json::from_str::<serde_json::Value>(&media_content) {
                if let Some(obj) = media_map.as_object() {
                    media_imported = obj.len();
                    std::fs::create_dir_all(&self.media_dir).ok();

                    for (key, val) in obj {
                        if let Some(real_filename) = val.as_str() {
                            if let Ok(mut zipped_media) = archive.by_name(key) {
                                let out_path = self.media_dir.join(real_filename);
                                if let Ok(mut out_file) = File::create(&out_path) {
                                    let _ = std::io::copy(&mut zipped_media, &mut out_file);
                                }
                            }
                        }
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