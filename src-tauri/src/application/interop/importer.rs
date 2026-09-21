use std::path::PathBuf;
use crate::domain::note::Note;
use rusqlite::Transaction;

pub enum ConflictResolution {
    Replace,
    Merge,
    Skip,
    Rename,
    Duplicate,
}

pub struct ImportResult {
    pub notes_imported: usize,
    pub media_imported: usize,
    pub duplicates_skipped: usize,
}

/// Abstract Trait for all Importers (NeoCards, CSV, APKG, Markdown)
pub trait Importer {
    fn validate(&self, path: &PathBuf) -> Result<(), String>;
    fn parse(&self, path: &PathBuf) -> Result<Vec<Note>, String>;
    fn import(&self, path: &PathBuf, tx: &Transaction, resolution: ConflictResolution) -> Result<ImportResult, String>;
}

/// The core orchestration engine for safely importing data
pub struct ImportEngine;

impl ImportEngine {
    pub fn execute(importer: Box<dyn Importer>, path: &PathBuf, tx: &Transaction, resolution: ConflictResolution) -> Result<ImportResult, String> {
        importer.validate(path)?;
        // Execute the atomic import within the provided SQLite transaction
        importer.import(path, tx, resolution)
    }
}