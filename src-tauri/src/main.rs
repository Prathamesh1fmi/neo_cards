#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod db;
mod commands;
mod domain;
mod infrastructure;

use std::sync::Mutex;
use tauri::Manager;
use infrastructure::desktop::fs::FileSystemService;

fn main() {
    tauri::Builder::default()
        .system_tray(infrastructure::desktop::tray::create_tray())
        .on_system_tray_event(infrastructure::desktop::tray::handle_tray_event)
        .setup(|app| {
            let fs_service = FileSystemService::new(&app.config());
            infrastructure::desktop::shortcuts::register_global_shortcuts(&app.handle());
            
            let db_path = fs_service.app_data.join("neocards.sqlite");
            let conn = db::connection::establish_connection(db_path).expect("Failed to connect to SQLite");
            db::migrations::run_migrations(&conn).expect("Failed to run migrations");

            app.manage(db::connection::DbState {
                conn: Mutex::new(conn),
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::deck_commands::create_deck,
            commands::deck_commands::get_deck_tree,
            commands::deck_commands::delete_deck
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}