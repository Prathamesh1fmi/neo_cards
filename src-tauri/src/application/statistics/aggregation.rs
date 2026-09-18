use rusqlite::Connection;
use crate::error::AppError;

pub struct AggregationPipeline;

impl AggregationPipeline {
    /// Designed to run in the background (or post-sync) to materialize heavy revlog queries
    /// into daily summary tables for instantaneous dashboard loading.
    pub fn run_daily_aggregation(conn: &Connection) -> Result<(), AppError> {
        conn.execute_batch(
            "
            CREATE TABLE IF NOT EXISTS revlog_daily_summary (
                date TEXT PRIMARY KEY,
                total_reviews INTEGER,
                again_count INTEGER,
                hard_count INTEGER,
                good_count INTEGER,
                easy_count INTEGER,
                total_time_ms INTEGER
            );
            
            -- Insert missing days via UPSERT
            INSERT INTO revlog_daily_summary (date, total_reviews, again_count, hard_count, good_count, easy_count, total_time_ms)
            SELECT 
                date(created_at, 'unixepoch'), 
                COUNT(*),
                SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END),
                SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END),
                SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END),
                SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END),
                SUM(time_taken_ms)
            FROM revlog
            WHERE date(created_at, 'unixepoch') = date('now', '-1 day')
            GROUP BY date(created_at, 'unixepoch')
            ON CONFLICT(date) DO UPDATE SET 
                total_reviews = excluded.total_reviews,
                total_time_ms = excluded.total_time_ms;
            "
        )?;
        Ok(())
    }
}