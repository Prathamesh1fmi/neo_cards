use std::path::PathBuf;
use rusqlite::Connection;

/// Abstract Trait for all Exporters
pub trait Exporter {
    fn export(&self, conn: &Connection, destination: &PathBuf) -> Result<(), String>;
}

pub struct ExportEngine;

impl ExportEngine {
    pub fn execute(exporter: Box<dyn Exporter>, conn: &Connection, destination: &PathBuf) -> Result<(), String> {
        exporter.export(conn, destination)
    }
}