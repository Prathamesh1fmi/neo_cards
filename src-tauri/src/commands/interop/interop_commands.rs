use tauri::{Window, State};
use crate::db::connection::DbState;
use std::path::PathBuf;
use crate::application::interop::{
    importer::{ImportEngine, ConflictResolution},
    parsers::CsvImporter,
};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct ImportRequest {
    pub file_path: String,
    pub format: String, // "csv", "apkg", "json"
    pub resolution: String, // "merge", "replace"
}

#[derive(Clone, Serialize)]
pub struct ProgressEvent {
    pub current: usize,
    pub total: usize,
    pub message: String,
}

#[tauri::command]
pub async fn start_import(req: ImportRequest, window: Window, state: State<'_, DbState>) -> Result<String, String> {
    let mut conn = state.conn.lock().unwrap();
    let tx = conn.transaction().map_err(|e| e.to_string())?;

    let path = PathBuf::from(&req.file_path);
    let deck_name = path.file_stem().unwrap_or_default().to_string_lossy().to_string();
    let deck_id = uuid::Uuid::new_v4().to_string();
    
    // Auto-create a deck for this import
    tx.execute(
        "INSERT INTO decks (id, parent_id, name, created_at) VALUES (?1, NULL, ?2, ?3)",
        rusqlite::params![deck_id, deck_name, chrono::Utc::now().timestamp()]
    ).map_err(|e| e.to_string())?;

    let importer: Box<dyn crate::application::interop::importer::Importer> = match req.format.as_str() {
        "csv" => Box::new(CsvImporter),
        "apkg" => Box::new(crate::application::interop::parsers::ApkgImporter {
            target_deck_id: deck_id, 
        }),
        _ => return Err("Unsupported format".to_string()),
    };

    let resolution = match req.resolution.as_str() {
        "replace" => ConflictResolution::Replace,
        _ => ConflictResolution::Merge, 
    };

    // Execute atomic import
    match ImportEngine::execute(importer, &path, &tx, resolution) {
        Ok(result) => {
            tx.commit().map_err(|e| e.to_string())?;
            let _ = window.emit("import_progress", ProgressEvent {
                current: 100,
                total: 100,
                message: "Import complete.".to_string(),
            });
            Ok(format!("Imported {} notes successfully", result.notes_imported))
        }
        Err(e) => {
            // Transaction drops and rolls back automatically
            Err(format!("Import failed: {}", e))
        }
    }
}