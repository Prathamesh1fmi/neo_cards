import React, { useState } from 'react';
import { RichTextEditor } from '../tiptap/RichTextEditor';
import { useQuery } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/tauri';
import { Save, Layout, Settings } from 'lucide-react';
import { motion } from 'framer-motion';

// Mocked NoteType for Milestone 3 UI
const MOCK_NOTE_TYPE = {
  id: "basic-1",
  name: "Basic",
  fields: [{ id: "f1", name: "Front", order: 1, required: true, type: "Text" }, { id: "f2", name: "Back", order: 2, required: false, type: "Text" }],
  templates: [{ id: "t1", name: "Card 1", front_html: "{{Front}}", back_html: "{{Front}}<hr id=answer>{{Back}}", css: ".card { text-align: center; }" }],
  created_at: Date.now()
};

export function EditorShell() {
  const [fields, setFields] = useState<Record<string, string>>({ "Front": "", "Back": "" });

  const { data: previews } = useQuery({
    queryKey: ['card-preview', fields],
    queryFn: () => invoke('preview_cards_live', { request: { note_type: MOCK_NOTE_TYPE, fields } }),
    // Debounce fast typing
    staleTime: 100,
  });

  return (
    <div className="flex h-full overflow-hidden bg-background">
      {/* LEFT: Field Editor Panel */}
      <div className="flex-1 flex flex-col border-r border-border overflow-y-auto">
        <div className="h-12 border-b border-border flex items-center px-4 justify-between bg-card shrink-0">
          <div className="font-medium text-sm">Add Note: Basic</div>
          <div className="flex gap-2">
            <button className="p-1.5 hover:bg-accent rounded text-muted-foreground"><Settings size={16}/></button>
          </div>
        </div>
        
        <div className="p-6 space-y-6 flex-1">
          {MOCK_NOTE_TYPE.fields.map(field => (
            <div key={field.id} className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex justify-between">
                <span>{field.name}</span>
                {field.required && <span className="text-destructive">*</span>}
              </label>
              <RichTextEditor 
                content={fields[field.name]}
                onChange={(html) => setFields(prev => ({...prev, [field.name]: html}))}
              />
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-border bg-card flex justify-end gap-2 shrink-0">
          <button className="px-4 py-2 text-sm font-medium border border-border rounded-md hover:bg-accent">Cancel</button>
          <button className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md flex items-center gap-2">
            <Save size={16} /> Save Note
          </button>
        </div>
      </div>

      {/* RIGHT: Live Preview Panel */}
      <div className="w-[400px] flex flex-col bg-muted/20 shrink-0">
        <div className="h-12 border-b border-border flex items-center px-4 gap-2 bg-card">
          <Layout size={16} className="text-muted-foreground" />
          <div className="font-medium text-sm">Live Preview</div>
        </div>
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {previews && Array.isArray(previews) && previews.map((preview: any) => (
            <motion.div initial={{opacity:0}} animate={{opacity:1}} key={preview.template_id} className="space-y-3">
              <div className="text-xs font-medium text-muted-foreground uppercase">{preview.template_name}</div>
              <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden divide-y divide-border">
                <div className="p-4 min-h-[100px] flex items-center justify-center" dangerouslySetInnerHTML={{__html: preview.front_compiled}}></div>
                <div className="p-4 min-h-[100px] flex items-center justify-center bg-muted/10" dangerouslySetInnerHTML={{__html: preview.back_compiled}}></div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}