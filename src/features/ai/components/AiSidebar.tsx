import React, { useState, useEffect, useRef } from 'react';
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