use crate::application::interop::importer::{Importer, ImportResult, ConflictResolution};
use std::path::PathBuf;
use rusqlite::Transaction;
use crate::domain::note::Note;

pub struct CsvImporter;
impl Importer for CsvImporter {
    fn validate(&self, _path: &PathBuf) -> Result<(), String> { Ok(()) }
    fn parse(&self, _path: &PathBuf) -> Result<Vec<Note>, String> { Ok(vec![]) }
    fn import(&self, _path: &PathBuf, _tx: &Transaction, _resolution: ConflictResolution) -> Result<ImportResult, String> {
        Ok(ImportResult { notes_imported: 0, media_imported: 0, duplicates_skipped: 0 })
    }
}

pub struct ApkgImporter;
impl Importer for ApkgImporter {
    fn validate(&self, _path: &PathBuf) -> Result<(), String> { Ok(()) }
    fn parse(&self, _path: &PathBuf) -> Result<Vec<Note>, String> { Ok(vec![]) }
    fn import(&self, _path: &PathBuf, _tx: &Transaction, _resolution: ConflictResolution) -> Result<ImportResult, String> {
        Ok(ImportResult { notes_imported: 0, media_imported: 0, duplicates_skipped: 0 })
    }
}