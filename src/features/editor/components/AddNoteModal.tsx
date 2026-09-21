import React, { useState } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import { X, Save, Layers } from "lucide-react";
import { RichTextEditor } from "@/features/editor/components/tiptap/RichTextEditor";

export function AddNoteModal({ isOpen, onClose, deckId, deckName }: { isOpen: boolean, onClose: () => void, deckId: string, deckName: string }) {
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");
  const [saving, setSaving] = useState(false);

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!front.trim()) return;
    setSaving(true);
    try {
      await invoke("add_note", { deckId, frontHtml: front, backHtml: back });
      setFront("");
      setBack("");
      // Don't close immediately so they can add another card rapidly
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-[600px] bg-card border border-border shadow-2xl rounded-xl flex flex-col overflow-hidden">
        
        <div className="h-12 border-b border-border flex items-center justify-between px-4 bg-muted/30">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Layers size={16} className="text-muted-foreground" /> Add Card to '{deckName}'
          </div>
          <button onClick={onClose} className="p-1.5 text-muted-foreground hover:bg-accent rounded-md"><X size={16} /></button>
        </div>

        <div className="p-6 space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground uppercase">Front (Question)</label>
            <RichTextEditor content={front} onChange={setFront} placeholder="What do you want to learn?" autoFocus />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground uppercase">Back (Answer)</label>
            <RichTextEditor content={back} onChange={setBack} placeholder="What is the answer?" />
          </div>
        </div>

        <div className="p-4 border-t border-border bg-muted/10 flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 text-sm font-medium hover:bg-accent rounded-md border border-transparent transition-colors">
            Close
          </button>
          <button 
            onClick={handleSave} 
            disabled={saving || !front.trim()}
            className="flex items-center gap-2 px-6 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            <Save size={16} /> {saving ? "Saving..." : "Add Card"}
          </button>
        </div>

      </div>
    </div>
  );
}
