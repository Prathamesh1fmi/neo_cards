use std::collections::HashMap;
use crate::application::plugins::manifest::PluginManifest;
use crate::error::AppError;

pub enum PluginState {
    Discovered,
    Validated,
    Loaded,
    Running,
    Crashed(String),
}

pub struct PluginContext {
    pub manifest: PluginManifest,
    pub state: PluginState,
}

pub struct PluginManager {
    plugins: HashMap<String, PluginContext>,
}

impl PluginManager {
    pub fn new() -> Self {
        Self { plugins: HashMap::new() }
    }

    pub fn discover(&mut self, plugin_dir: &std::path::Path) -> Result<(), AppError> {
        // MOCK: Reads plugin.json from directories, validates schema, checks core version compatibility.
        Ok(())
    }

    pub fn load_plugin(&mut self, plugin_id: &str) -> Result<(), AppError> {
        // MOCK: Verifies permissions, sandboxes execution environment (e.g. Deno/V8 or WASM), executes entrypoint.
        Ok(())
    }
}