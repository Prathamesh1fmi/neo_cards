import os
from pathlib import Path

base = Path('.')

dirs = [
    'src-tauri/src/infrastructure/desktop',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

scripts['src-tauri/Cargo.toml'] = r'''[package]
name = "neocards"
version = "0.1.0"
description = "A local-first learning platform"
authors = ["NeoCards Team"]
edition = "2021"

[build-dependencies]
tauri-build = { version = "1.5", features = [] }

[dependencies]
tauri = { version = "1.5", features = [
    "shell-open", 
    "dialog-all", 
    "fs-all", 
    "global-shortcut-all", 
    "notification-all", 
    "system-tray", 
    "updater", 
    "window-all",
    "path-all"
] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
rusqlite = { version = "0.31.0", features = ["bundled"] }
uuid = { version = "1.8", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }
thiserror = "1.0"
tauri-plugin-window-state = "0.1"
tauri-plugin-log = "0.1"
log = "0.4"

[features]
custom-protocol = ["tauri/custom-protocol"]
'''

scripts['src-tauri/tauri.conf.json'] = r'''{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:1420",
    "distDir": "../dist",
    "withGlobalTauri": false
  },
  "package": {
    "productName": "NeoCards",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": { "all": false, "open": true },
      "dialog": { "all": true },
      "fs": { "all": true, "scope": ["$APPDATA/**", "$DOWNLOAD/**"] },
      "globalShortcut": { "all": true },
      "notification": { "all": true },
      "path": { "all": true },
      "window": { "all": true }
    },
    "bundle": {
      "active": true,
      "targets": "all",
      "identifier": "com.neocards.dev",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ]
    },
    "security": { "csp": null },
    "updater": {
      "active": true,
      "endpoints": ["https://api.neocards.dev/update/{{target}}/{{current_version}}"],
      "dialog": true,
      "pubkey": ""
    },
    "systemTray": {
      "iconPath": "icons/icon.ico",
      "iconAsTemplate": true
    },
    "windows": [
      {
        "fullscreen": false,
        "resizable": true,
        "title": "NeoCards",
        "width": 1200,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600,
        "hiddenTitle": true,
        "titleBarStyle": "Overlay",
        "decorations": false,
        "transparent": true
      }
    ]
  }
}'''

scripts['src-tauri/src/infrastructure/mod.rs'] = r'''pub mod deck_repository;
pub mod desktop;
'''

scripts['src-tauri/src/infrastructure/desktop/mod.rs'] = r'''pub mod tray;
pub mod window_manager;
pub mod notifications;
pub mod fs;
pub mod dialog;
pub mod updater;
pub mod shortcuts;
'''

scripts['src-tauri/src/infrastructure/desktop/tray.rs'] = r'''use tauri::{AppHandle, CustomMenuItem, SystemTray, SystemTrayEvent, SystemTrayMenu, SystemTrayMenuItem};
use tauri::Manager;

pub fn create_tray() -> SystemTray {
    let open = CustomMenuItem::new("open".to_string(), "Open NeoCards");
    let review = CustomMenuItem::new("review".to_string(), "Start Review");
    let capture = CustomMenuItem::new("capture".to_string(), "Quick Capture");
    let settings = CustomMenuItem::new("settings".to_string(), "Settings");
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");

    let tray_menu = SystemTrayMenu::new()
        .add_item(open)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(review)
        .add_item(capture)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(settings)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    SystemTray::new().with_menu(tray_menu)
}

pub fn handle_tray_event(app: &AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::MenuItemClick { id, .. } => {
            match id.as_str() {
                "quit" => { std::process::exit(0); }
                "open" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                _ => {}
            }
        }
        SystemTrayEvent::DoubleClick { .. } => {
            let window = app.get_window("main").unwrap();
            window.show().unwrap();
            window.set_focus().unwrap();
        }
        _ => {}
    }
}
'''

scripts['src-tauri/src/infrastructure/desktop/shortcuts.rs'] = r'''use tauri::{AppHandle, GlobalShortcutManager, Manager};

pub fn register_global_shortcuts(app: &AppHandle) {
    let mut manager = app.global_shortcut_manager();
    
    // Command Palette (Ctrl+K is typically handled inside the frontend, 
    // but if we want it global when app is minimized, we register it here)
    let _ = manager.register("CmdOrCtrl+K", || {
        log::info!("Global shortcut: Command Palette Triggered");
    });

    let _ = manager.register("CmdOrCtrl+Shift+R", || {
        log::info!("Global shortcut: Start Review Triggered");
    });

    let _ = manager.register("CmdOrCtrl+Shift+N", || {
        log::info!("Global shortcut: New Note Triggered");
    });
}
'''

scripts['src-tauri/src/infrastructure/desktop/fs.rs'] = r'''use std::path::PathBuf;
use tauri::api::path::{app_data_dir, app_log_dir};
use tauri::Config;

pub struct FileSystemService {
    pub app_data: PathBuf,
    pub backups: PathBuf,
    pub logs: PathBuf,
    pub plugins: PathBuf,
    pub imports: PathBuf,
    pub exports: PathBuf,
    pub temp: PathBuf,
}

impl FileSystemService {
    pub fn new(config: &Config) -> Self {
        let app_data = app_data_dir(config).expect("Failed to resolve app data dir");
        let backups = app_data.join("backups");
        let logs = app_log_dir(config).unwrap_or_else(|| app_data.join("logs"));
        let plugins = app_data.join("plugins");
        let imports = app_data.join("imports");
        let exports = app_data.join("exports");
        let temp = app_data.join("temp");

        std::fs::create_dir_all(&app_data).ok();
        std::fs::create_dir_all(&backups).ok();
        std::fs::create_dir_all(&logs).ok();
        std::fs::create_dir_all(&plugins).ok();
        std::fs::create_dir_all(&imports).ok();
        std::fs::create_dir_all(&exports).ok();
        std::fs::create_dir_all(&temp).ok();

        Self {
            app_data,
            backups,
            logs,
            plugins,
            imports,
            exports,
            temp,
        }
    }
}
'''

scripts['src-tauri/src/main.rs'] = r'''#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod db;
mod commands;
mod domain;
mod infrastructure;

use std::sync::Mutex;
use tauri::Manager;
use infrastructure::desktop::fs::FileSystemService;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_window_state::Builder::default().build())
        .plugin(tauri_plugin_log::Builder::default()
            .targets([
                tauri_plugin_log::LogTarget::LogDir,
                tauri_plugin_log::LogTarget::Stdout,
            ])
            .build()
        )
        .system_tray(infrastructure::desktop::tray::create_tray())
        .on_system_tray_event(infrastructure::desktop::tray::handle_tray_event)
        .setup(|app| {
            // Logging startup
            log::info!("NeoCards starting up...");

            // File System Service Initialization
            let fs_service = FileSystemService::new(&app.config());
            
            // Global Shortcuts
            infrastructure::desktop::shortcuts::register_global_shortcuts(&app.handle());
            
            let db_path = fs_service.app_data.join("neocards.sqlite");
            
            // Initialize connection and run migrations
            let conn = db::connection::establish_connection(db_path).expect("Failed to connect to SQLite");
            db::migrations::run_migrations(&conn).expect("Failed to run migrations");

            app.manage(db::connection::DbState {
                conn: Mutex::new(conn),
            });

            log::info!("Startup complete.");
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

print("Desktop Native Scaffolding complete.")

