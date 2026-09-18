use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AiMessage {
    pub role: String, // "system", "user", "assistant"
    pub content: String,
}

pub trait AiProvider {
    /// Generates a response based on a prompt.
    /// In a production environment, this would return a stream or a Channel Receiver.
    fn generate_stream(&self, messages: Vec<AiMessage>) -> Result<std::sync::mpsc::Receiver<String>, String>;
    
    /// Generates vector embeddings for a given text
    fn generate_embeddings(&self, text: &str) -> Result<Vec<f32>, String>;
}