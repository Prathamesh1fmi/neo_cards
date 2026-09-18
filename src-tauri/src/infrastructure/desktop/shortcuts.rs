use tauri::{AppHandle, GlobalShortcutManager, Manager};

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