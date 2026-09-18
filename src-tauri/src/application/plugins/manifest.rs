use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginManifest {
    pub id: String,
    pub name: String,
    pub author: String,
    pub description: String,
    pub version: String,
    pub minimum_core_version: String,
    pub maximum_core_version: Option<String>,
    pub permissions: Vec<Permission>,
    pub entrypoint: String,
    pub icon: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum Permission {
    FileSystem,
    Media,
    DatabaseRead,
    DatabaseWrite,
    ReviewEngine,
    CommandPalette,
    Notifications,
}