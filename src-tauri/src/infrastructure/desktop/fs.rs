use std::path::PathBuf;
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