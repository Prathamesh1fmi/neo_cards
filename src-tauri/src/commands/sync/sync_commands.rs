use tauri::{State, Window};
use crate::db::connection::DbState;
use serde::Serialize;

#[derive(Serialize)]
pub struct SyncStatusDto {
    pub status: String,
    pub pending_changes: usize,
    pub last_sync: Option<String>,
}

#[tauri::command]
pub async fn trigger_manual_sync(window: Window, state: State<'_, DbState>) -> Result<(), String> {
    // Emit progress event
    let _ = window.emit("sync_event", "SyncStarted");
    let _ = window.emit("sync_event", "Uploading");
    
    // MOCK background delay
    // std::thread::sleep(std::time::Duration::from_millis(500));
    
    let _ = window.emit("sync_event", "Completed");
    Ok(())
}

#[tauri::command]
pub fn get_sync_status(state: State<DbState>) -> Result<SyncStatusDto, String> {
    Ok(SyncStatusDto {
        status: "idle".to_string(),
        pending_changes: 14,
        last_sync: Some("2 mins ago".to_string()),
    })
}