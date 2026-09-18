import os
from pathlib import Path

base = Path('.')

dirs = [
    'docs/adr',
    'src-tauri/src/application/ai',
    'src-tauri/src/domain/ai',
    'src-tauri/src/infrastructure/ai',
    'src-tauri/src/commands/ai',
    'src/features/ai/components',
    'src/features/ai/hooks',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. Architecture Decision Records
scripts['docs/adr/0014-ai-architecture.md'] = '''# ADR 0014: AI Architecture & Privacy
## Context
Users want intelligent features (card generation, summarization) but demand strict privacy for their notes.
## Decision
AI processing is completely decoupled from React. Rust acts as the orchestrator. We support three modes: Cloud (OpenAI/Anthropic), Local (Ollama/LM Studio), and Offline-Only (Disabled). The user explicitly selects their provider. NeoCards is purely a client.
'''

scripts['docs/adr/0015-rag-pipeline.md'] = '''# ADR 0015: RAG Pipeline
## Context
LLMs cannot fit 100,000 notes into their context window.
## Decision
We implement Retrieval-Augmented Generation (RAG). Before querying the LLM, Rust queries SQLite FTS5 and the Embedding cache to find the top 5 most relevant notes. Only these specific, ranked chunks are injected into the Prompt Builder.
'''

# 2. Rust Domain & Provider Trait
scripts['src-tauri/src/application/ai/mod.rs'] = r'''pub mod provider;
pub mod orchestrator;
pub mod prompt_builder;
pub mod retrieval;
pub mod embeddings;
'''

scripts['src-tauri/src/application/ai/provider.rs'] = r'''use serde::{Deserialize, Serialize};

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
'''

scripts['src-tauri/src/infrastructure/ai/mod.rs'] = r'''pub mod ollama_provider;
pub mod openai_provider;
'''

scripts['src-tauri/src/infrastructure/ai/ollama_provider.rs'] = r'''use crate::application::ai::provider::{AiProvider, AiMessage};
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
'''

# 3. AI Orchestrator & RAG
scripts['src-tauri/src/application/ai/orchestrator.rs'] = r'''use crate::application::ai::provider::{AiProvider, AiMessage};
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
'''

# 4. IPC Commands (Streaming to React)
scripts['src-tauri/src/commands/ai/mod.rs'] = r'''pub mod ai_commands;'''

scripts['src-tauri/src/commands/ai/ai_commands.rs'] = r'''use tauri::{Window, State};
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
'''

# 5. React AI Workspace
scripts['src/features/ai/components/AiSidebar.tsx'] = r'''import React, { useState, useEffect, useRef } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import { Bot, Send, BrainCircuit, ShieldCheck, Settings } from 'lucide-react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export function AiSidebar() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const unlistenToken = listen('ai_token', (event) => {
      const token = event.payload as string;
      setMessages(prev => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant') {
          return [...prev.slice(0, -1), { role: 'assistant', content: last.content + token }];
        } else {
          return [...prev, { role: 'assistant', content: token }];
        }
      });
    });

    const unlistenDone = listen('ai_done', () => {
      setIsGenerating(false);
    });

    return () => {
      unlistenToken.then(f => f());
      unlistenDone.then(f => f());
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isGenerating) return;
    const query = input;
    setInput("");
    setMessages(prev => [...prev, { role: 'user', content: query }]);
    setIsGenerating(true);

    try {
      await invoke('send_ai_query', { query });
    } catch (e) {
      console.error(e);
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col h-full w-80 bg-card border-l border-border shrink-0">
      <div className="h-12 border-b border-border flex items-center px-4 justify-between bg-card">
        <div className="flex items-center gap-2 font-medium text-sm">
          <BrainCircuit size={16} className="text-primary" /> Copilot
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-[10px] uppercase font-bold text-green-500 bg-green-500/10 px-1.5 py-0.5 rounded">
            <ShieldCheck size={12}/> Local AI
          </div>
          <button className="text-muted-foreground hover:text-foreground"><Settings size={14}/></button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground space-y-4 opacity-70">
            <Bot size={48} />
            <div className="text-sm">I'm connected to your local Ollama instance.<br/>Ask me to generate flashcards, summarize notes, or explain concepts.</div>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`px-3 py-2 rounded-xl max-w-[85%] text-sm ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted/50 border border-border text-foreground'}`}>
              {msg.content}
            </div>
            {msg.role === 'assistant' && !isGenerating && i === messages.length -1 && (
               <div className="text-[10px] text-muted-foreground mt-1 ml-1 flex gap-2">
                  <span className="hover:underline cursor-pointer">Generate Cards</span>
                  <span className="hover:underline cursor-pointer">Append to Note</span>
               </div>
            )}
          </div>
        ))}
        {isGenerating && (
          <div className="text-muted-foreground animate-pulse text-xs ml-1">Generating response...</div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-3 border-t border-border bg-card">
        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Ask AI..."
            className="w-full bg-background border border-border rounded-lg pl-3 pr-10 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary min-h-[44px] max-h-32 resize-none"
            rows={1}
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim() || isGenerating}
            className="absolute right-2 bottom-2.5 p-1 bg-primary text-primary-foreground rounded-md disabled:opacity-50 hover:bg-primary/90 transition-colors"
          >
            <Send size={14} />
          </button>
        </div>
        <div className="text-[10px] text-muted-foreground text-center mt-2">
          Model: llama3 • Context Window: 8192
        </div>
      </div>
    </div>
  );
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("AI Knowledge Platform Scaffolding complete.")

