import React, { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

export function CommandPalette() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  if (!open) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-background/80 backdrop-blur-sm"
          onClick={() => setOpen(false)}
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="relative w-full max-w-lg rounded-xl border border-border bg-card shadow-2xl overflow-hidden"
        >
          <div className="flex items-center border-b border-border px-4 py-3">
            <Search className="mr-2 h-5 w-5 shrink-0 text-muted-foreground" />
            <input 
              autoFocus 
              className="flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="Type a command or search..."
            />
          </div>
          <div className="max-h-80 overflow-y-auto p-2">
            <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">Suggestions</div>
            <div className="px-2 py-2 text-sm text-foreground hover:bg-accent rounded-md cursor-pointer flex items-center justify-between">
              <span>Create New Deck</span>
              <kbd className="text-xs bg-muted px-1.5 py-0.5 rounded border border-border">C</kbd>
            </div>
            <div className="px-2 py-2 text-sm text-foreground hover:bg-accent rounded-md cursor-pointer flex items-center justify-between">
              <span>Review Due Cards</span>
              <kbd className="text-xs bg-muted px-1.5 py-0.5 rounded border border-border">Space</kbd>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}