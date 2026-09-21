import React, { useState } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { deckApi, DeckTree } from "@/features/decks/api/deckCommands";
import { Layers, Plus, Trash2, Folder, ChevronRight, ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

function DeckNode({ node, onDelete }: { node: DeckTree, onDelete: (id: string) => void }) {
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
        <span className="flex-1">{node.deck.name}</span>
        
        <button 
          onClick={(e) => { e.stopPropagation(); onDelete(node.deck.id); }}
          className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive hover:bg-destructive/10 rounded"
        >
          <Trash2 size={12} />
        </button>
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
              <DeckNode key={child.deck.id} node={child} onDelete={onDelete} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function Decks() {
  const queryClient = useQueryClient();
  const [newDeckName, setNewDeckName] = useState("");

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

  return (
    <PageContainer title="Decks Explorer">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 h-full">
        <div className="col-span-1 md:col-span-3 bg-card border border-border rounded-xl p-4 min-h-[500px]">
          <div className="flex items-center gap-2 mb-4 pb-2 border-b border-border">
            <input 
              type="text"
              placeholder="New Deck Name..."
              value={newDeckName}
              onChange={(e) => setNewDeckName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
              className="flex-1 bg-transparent text-sm outline-none px-2 py-1"
            />
            <button 
              onClick={handleCreate}
              className="p-1 hover:bg-accent rounded-md text-muted-foreground"
            >
              <Plus size={16} />
            </button>
          </div>

          {isLoading ? (
            <div className="animate-pulse space-y-2">
              <div className="h-6 bg-muted rounded w-3/4"></div>
              <div className="h-6 bg-muted rounded w-1/2"></div>
            </div>
          ) : tree?.length === 0 ? (
            <div className="text-center py-10 text-muted-foreground text-sm">
              No decks found. Create one above.
            </div>
          ) : (
            <div className="space-y-1">
              {tree?.map(node => (
                <DeckNode key={node.deck.id} node={node} onDelete={(id) => deleteMutation.mutate(id)} />
              ))}
            </div>
          )}
        </div>
      </div>
    </PageContainer>
  );
}