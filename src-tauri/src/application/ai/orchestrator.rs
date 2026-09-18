use crate::application::ai::provider::{AiProvider, AiMessage};
use rusqlite::Connection;
use std::sync::mpsc;

pub struct AiOrchestrator {
    pub provider: Box<dyn AiProvider + Send + Sync>,
}

impl AiOrchestrator {
    pub fn new(provider: Box<dyn AiProvider + Send + Sync>) -> Self {
        Self { provider }
    }

    /// RAG Pipeline: FTS Retrieval -> Prompt Building -> Stream Generation
    pub fn process_query(&self, conn: &Connection, user_query: &str) -> Result<mpsc::Receiver<String>, String> {
        // 1. Retrieval (Mock)
        // let relevant_notes = retrieval::search_fts_and_vector(conn, user_query);
        let retrieved_context = "Note ID: 123. Context: The mitochondria is the powerhouse of the cell.";

        // 2. Prompt Building
        let system_prompt = format!("
            You are the NeoCards Learning Assistant. 
            Use the following retrieved notes to answer the user's query.
            Retrieved Context: {}
        ", retrieved_context);

        let messages = vec![
            AiMessage { role: "system".to_string(), content: system_prompt },
            AiMessage { role: "user".to_string(), content: user_query.to_string() },
        ];

        // 3. Execution (Streams back)
        self.provider.generate_stream(messages)
    }
}