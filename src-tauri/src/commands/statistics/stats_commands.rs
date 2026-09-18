use tauri::State;
use crate::db::connection::DbState;
use crate::error::AppError;
use crate::application::statistics::engine::{StatisticsEngine, GeneralAnalytics, HeatmapData};
use crate::application::statistics::fsrs_analytics::{FsrsAnalyticsEngine, FsrsMetrics};

#[tauri::command]
pub fn get_general_analytics(state: State<DbState>) -> Result<GeneralAnalytics, AppError> {
    let conn = state.conn.lock().unwrap();
    StatisticsEngine::get_general_analytics(&conn)
}

#[tauri::command]
pub fn get_fsrs_metrics(deck_id: String, state: State<DbState>) -> Result<FsrsMetrics, AppError> {
    let conn = state.conn.lock().unwrap();
    FsrsAnalyticsEngine::calculate_deck_health(&conn, &deck_id)
}

#[tauri::command]
pub fn get_heatmap_data(year: i32, state: State<DbState>) -> Result<Vec<HeatmapData>, AppError> {
    let conn = state.conn.lock().unwrap();
    StatisticsEngine::get_heatmap(&conn, year)
}