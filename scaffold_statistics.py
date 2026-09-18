import os
from pathlib import Path

base = Path('.')

dirs = [
    'src-tauri/src/application/statistics',
    'src-tauri/src/commands/statistics',
    'src/features/statistics/components/charts',
    'src/features/statistics/api',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. Rust Statistics Architecture
scripts['src-tauri/src/application/statistics/mod.rs'] = r'''pub mod engine;
pub mod fsrs_analytics;
pub mod aggregation;
'''

# 2. Core Statistics Engine
scripts['src-tauri/src/application/statistics/engine.rs'] = r'''use serde::Serialize;
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
'''

# 3. FSRS Analytics Engine
scripts['src-tauri/src/application/statistics/fsrs_analytics.rs'] = r'''use serde::Serialize;
use rusqlite::Connection;
use crate::error::AppError;

#[derive(Serialize)]
pub struct FsrsMetrics {
    pub average_stability: f64,
    pub average_difficulty: f64,
    pub mature_cards: i32,
    pub young_cards: i32,
    pub estimated_retrievability: f64,
}

pub struct FsrsAnalyticsEngine;

impl FsrsAnalyticsEngine {
    /// Calculates the overall memory health of a specific deck based on FSRS metrics
    pub fn calculate_deck_health(conn: &Connection, deck_id: &str) -> Result<FsrsMetrics, AppError> {
        // MOCK: In production, this runs AVG(stability), AVG(difficulty) over the cards table
        // Retrievability is modeled as R = 900^-(elapsed_days / stability)
        Ok(FsrsMetrics {
            average_stability: 21.5,
            average_difficulty: 5.2,
            mature_cards: 450,
            young_cards: 120,
            estimated_retrievability: 89.2,
        })
    }
}
'''

# 4. Aggregation Pipeline
scripts['src-tauri/src/application/statistics/aggregation.rs'] = r'''use rusqlite::Connection;
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
'''

# 5. IPC Commands
scripts['src-tauri/src/commands/statistics/mod.rs'] = r'''pub mod stats_commands;'''
scripts['src-tauri/src/commands/statistics/stats_commands.rs'] = r'''use tauri::State;
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
'''

# 6. React Dashboard (Linear/Stripe Style)
scripts['src/features/statistics/components/Dashboard.tsx'] = r'''import React from 'react';
import { HeatmapChart } from './charts/HeatmapChart';
import { Activity, Brain, Target, Clock, Zap } from 'lucide-react';

export function Dashboard() {
  return (
    <div className="flex flex-col h-full w-full bg-background overflow-y-auto pt-8 pb-12 px-6 sm:px-12 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Intelligence</h1>
          <p className="text-sm text-muted-foreground mt-1">Your learning analytics and memory health.</p>
        </div>
        <div className="flex gap-2">
          <select className="bg-card border border-border text-sm rounded-md px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary">
            <option>All Decks</option>
            <option>Biology</option>
            <option>Spanish</option>
          </select>
          <select className="bg-card border border-border text-sm rounded-md px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary">
            <option>Last 30 Days</option>
            <option>This Year</option>
            <option>All Time</option>
          </select>
        </div>
      </div>

      {/* KPI Cards (Stripe Style) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard title="Total Reviews" value="14,205" trend="+12% this week" icon={<Activity size={16} />} />
        <MetricCard title="Retention Rate" value="87.5%" trend="Optimal range" icon={<Target size={16} />} />
        <MetricCard title="Current Streak" value="12 Days" trend="Longest: 45 days" icon={<Zap size={16} />} />
        <MetricCard title="Avg. Review Time" value="4.5s" trend="-0.2s this week" icon={<Clock size={16} />} />
      </div>

      {/* Main Charts Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 shadow-sm">
          <h3 className="text-sm font-semibold mb-4">Review Heatmap</h3>
          <HeatmapChart />
        </div>
        
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col">
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Brain size={16} className="text-primary" /> FSRS Memory State
          </h3>
          <div className="flex-1 space-y-6 mt-2">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Estimated Retrievability</span>
                <span className="font-medium text-green-500">89.2%</span>
              </div>
              <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden"><div className="h-full bg-green-500 w-[89.2%]"></div></div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground mb-1">Avg. Stability</div>
                <div className="font-medium text-xl">21.5d</div>
              </div>
              <div>
                <div className="text-muted-foreground mb-1">Avg. Difficulty</div>
                <div className="font-medium text-xl">5.2</div>
              </div>
              <div>
                <div className="text-muted-foreground mb-1">Mature Cards</div>
                <div className="font-medium text-xl">450</div>
              </div>
              <div>
                <div className="text-muted-foreground mb-1">Young Cards</div>
                <div className="font-medium text-xl">120</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, trend, icon }: any) {
  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between text-muted-foreground mb-3">
        <span className="text-sm font-medium">{title}</span>
        {icon}
      </div>
      <div className="text-3xl font-semibold tracking-tight mb-1">{value}</div>
      <div className="text-xs text-muted-foreground">{trend}</div>
    </div>
  );
}
'''

# 7. Mock Heatmap Component
scripts['src/features/statistics/components/charts/HeatmapChart.tsx'] = r'''import React from 'react';

// For Milestone 9, we scaffold the visual representation.
// In production, this uses an Area Chart or GitHub-style calendar SVG
export function HeatmapChart() {
  return (
    <div className="w-full h-[200px] flex items-center justify-center bg-muted/20 border border-dashed border-border rounded-md">
      <span className="text-sm text-muted-foreground">Heatmap / Chart rendering visualization goes here (via Rust pre-aggregated data)</span>
    </div>
  );
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Statistics Engine Scaffolding complete.")

