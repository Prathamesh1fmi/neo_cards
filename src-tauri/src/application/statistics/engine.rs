use serde::Serialize;
use rusqlite::Connection;
use crate::error::AppError;

#[derive(Serialize)]
pub struct HeatmapData {
    pub date: String,
    pub count: i32,
}

#[derive(Serialize)]
pub struct GeneralAnalytics {
    pub total_reviews: i32,
    pub retention_rate: f64,
    pub current_streak: i32,
    pub longest_streak: i32,
    pub average_review_time_ms: i32,
}

pub struct StatisticsEngine;

impl StatisticsEngine {
    /// Retrieves pre-aggregated overview statistics without doing heavy table scans
    pub fn get_general_analytics(conn: &Connection) -> Result<GeneralAnalytics, AppError> {
        // MOCK: Queries from pre-aggregated tables or materialized views
        Ok(GeneralAnalytics {
            total_reviews: 14205,
            retention_rate: 87.5,
            current_streak: 12,
            longest_streak: 45,
            average_review_time_ms: 4500,
        })
    }

    /// Fetches time-series data for the GitHub-style contribution heatmap
    pub fn get_heatmap(conn: &Connection, year: i32) -> Result<Vec<HeatmapData>, AppError> {
        Ok(vec![
            HeatmapData { date: "2024-10-01".to_string(), count: 150 },
            HeatmapData { date: "2024-10-02".to_string(), count: 210 },
        ])
    }
}