use tauri::{Window, State};
use crate::db::connection::DbState;
use crate::application::ai::orchestrator::AiOrchestrator;
use crate::infrastructure::ai::ollama_provider::OllamaProvider;

#[tauri::command]
pub async fn send_ai_query(query: String, window: Window, state: State<'_, DbState>) -> Result<(), String> {
    // In production, the provider is selected dynamically via App Config
    let provider = Box::new(OllamaProvider {
        endpoint: "http://localhost:11434".to_string(),
        model: "llama3".to_string(),
    });
    
    let orchestrator = AiOrchestrator::new(provider);
    
    let conn = state.conn.lock().unwrap();
    let rx = orchestrator.process_query(&conn, &query)?;
    
    // Spawn a thread to forward tokens to the React frontend
    std::thread::spawn(move || {
        while let Ok(token) = rx.recv() {
            let _ = window.emit("ai_token", token);
        }
        let _ = window.emit("ai_done", ());
    });
    
    Ok(())
}