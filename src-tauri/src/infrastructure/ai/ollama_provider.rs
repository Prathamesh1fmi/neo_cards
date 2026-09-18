use crate::application::ai::provider::{AiProvider, AiMessage};
use std::sync::mpsc;
use std::thread;

pub struct OllamaProvider {
    pub endpoint: String,
    pub model: String,
}

impl AiProvider for OllamaProvider {
    fn generate_stream(&self, _messages: Vec<AiMessage>) -> Result<mpsc::Receiver<String>, String> {
        let (tx, rx) = mpsc::channel();
        
        // MOCK: Simulate token streaming from a local Ollama instance
        thread::spawn(move || {
            let tokens = vec!["I ", "have ", "analyzed ", "your ", "notes ", "and ", "generated ", "flashcards."];
            for token in tokens {
                tx.send(token.to_string()).unwrap();
                thread::sleep(std::time::Duration::from_millis(150));
            }
        });
        
        Ok(rx)
    }

    fn generate_embeddings(&self, _text: &str) -> Result<Vec<f32>, String> {
        Ok(vec![0.1, 0.2, 0.3]) // MOCK
    }
}