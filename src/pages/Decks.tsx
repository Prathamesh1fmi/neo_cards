import React, { useState } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { deckApi, DeckTree } from "@/features/decks/api/deckCommands";
import { Plus, Trash2, Folder, ChevronRight, ChevronDown, Play, Settings, FileUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { ImportDialog } from "@/features/interop/components/ImportDialog";
import { DeckSettingsModal } from "@/features/decks/components/DeckSettingsModal";

function DeckNode({ node, onDelete, onStudy, onSettings }: { node: DeckTree, onDelete: (id: string) => void, onStudy: (id: string) => void, onSettings: (id: string) => void }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className="select-none">
      <div 
        className="flex items-center gap-2 py-1.5 px-2 hover:bg-accent rounded-md cursor-pointer group text-sm"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="w-4 h-4 flex items-center justify-center text-muted-foreground">
          {node.children.length > 0 && (expanded ? <ChevronDown size={14}/> : <ChevronRight size={14}/>)}
        </span>
        <Folder size={14} className="text-muted-foreground" />
        <span className="flex-1 font-medium">{node.deck.name}</span>
        
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            onClick={(e) => { e.stopPropagation(); onStudy(node.deck.id); }}
            className="p-1.5 text-primary hover:bg-primary/10 rounded"
            title="Study Deck"
          >
            <Play size={14} className="fill-primary" />
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); onSettings(node.deck.id); }}
            className="p-1.5 text-muted-foreground hover:bg-accent rounded"
            title="Deck Settings"
          >
            <Settings size={14} />
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); onDelete(node.deck.id); }}
            className="p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded"
            title="Delete Deck"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
      
      <AnimatePresence>
        {expanded && node.children.length > 0 && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="ml-6 border-l border-border pl-2 overflow-hidden"
          >
            {node.children.map(child => (
              <DeckNode key={child.deck.id} node={child} onDelete={onDelete} onStudy={onStudy} onSettings={onSettings} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function Decks() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [newDeckName, setNewDeckName] = useState("");
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [settingsDeckId, setSettingsDeckId] = useState<string | null>(null);

  const { data: tree, isLoading } = useQuery({
    queryKey: ['decks'],
    queryFn: deckApi.getDeckTree
  });

  const createMutation = useMutation({
    mutationFn: () => deckApi.createDeck(newDeckName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decks'] });
      setNewDeckName("");
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deckApi.deleteDeck(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['decks'] })
  });

  const handleCreate = () => {
    if (newDeckName.trim() === "") return;
    createMutation.mutate();
  };

  const handleStudy = (id: string) => {
    navigate(`/review?deckId=${id}`);
  };

  return (
    <PageContainer title="Decks Explorer">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 h-full">
        <div className="col-span-1 md:col-span-3 bg-card border border-border rounded-xl p-4 min-h-[500px] flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-border gap-4">
            <div className="flex-1 flex items-center gap-2 bg-background border border-border rounded-md px-2 focus-within:ring-1 ring-primary transition-shadow">
              <input 
                type="text"
                placeholder="New Deck Name..."
                value={newDeckName}
                onChange={(e) => setNewDeckName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
                className="flex-1 bg-transparent text-sm outline-none py-1.5"
              />
              <button 
                onClick={handleCreate}
                className="p-1 hover:bg-accent rounded-md text-muted-foreground"
              >
                <Plus size={16} />
              </button>
            </div>
            
            <button 
              onClick={() => setIsImportOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-secondary text-secondary-foreground text-sm font-medium rounded-md hover:bg-secondary/80 border border-border transition-colors shrink-0"
            >
              <FileUp size={16} /> Import
            </button>
          </div>

          <div className="flex-1 overflow-y-auto">
            {isLoading ? (
              <div className="animate-pulse space-y-2 mt-4">
                <div className="h-6 bg-muted rounded w-3/4"></div>
                <div className="h-6 bg-muted rounded w-1/2"></div>
              </div>
            ) : tree?.length === 0 ? (
              <div className="text-center py-16 flex flex-col items-center justify-center space-y-3">
                <Folder size={48} className="text-muted-foreground/30" />
                <div className="text-muted-foreground text-sm">No decks found. Create one or import an .apkg file.</div>
              </div>
            ) : (
              <div className="space-y-1 mt-2">
                {tree?.map(node => (
                  <DeckNode key={node.deck.id} node={node} onDelete={(id) => deleteMutation.mutate(id)} onStudy={handleStudy} onSettings={(id) => setSettingsDeckId(id)} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      <ImportDialog isOpen={isImportOpen} onClose={() => { setIsImportOpen(false); queryClient.invalidateQueries({ queryKey: ['decks'] }); }} />
      {settingsDeckId && (
        <DeckSettingsModal isOpen={!!settingsDeckId} onClose={() => setSettingsDeckId(null)} deckId={settingsDeckId} />
      )}
    </PageContainer>
  );
}