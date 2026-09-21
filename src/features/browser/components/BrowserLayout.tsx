import React, { useState } from 'react';
import { Search, Filter, Tag, Layers, Star, Database } from 'lucide-react';
import { VirtualizedGrid } from './VirtualizedGrid';

export function BrowserLayout() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="flex h-full w-full bg-background overflow-hidden">
      
      {/* LEFT PANEL: Navigator */}
      <div className="w-64 border-r border-border bg-card/50 flex flex-col shrink-0">
        <div className="p-4 border-b border-border">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search anything..." 
              className="w-full bg-background border border-border rounded-md pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-4">
          <div>
            <div className="text-xs font-semibold text-muted-foreground uppercase px-2 mb-1">Collections</div>
            <div className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded cursor-pointer"><Layers size={14}/> All Notes</div>
            <div className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded cursor-pointer"><Star size={14}/> Favorites</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-muted-foreground uppercase px-2 mb-1">Tags</div>
            <div className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded cursor-pointer"><Tag size={14}/> #biology</div>
            <div className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent rounded cursor-pointer"><Tag size={14}/> #spanish</div>
          </div>
        </div>
      </div>

      {/* CENTER PANEL: Grid */}
      <div className="flex-1 flex flex-col min-w-0 bg-background">
        <div className="h-12 border-b border-border flex items-center px-4 justify-between bg-card">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Database size={16} className="text-muted-foreground" />
            Search Results
          </div>
          <div className="flex gap-2">
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm border border-border rounded-md hover:bg-accent">
              <Filter size={14} /> Filter
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-hidden">
          <VirtualizedGrid query={searchQuery} />
        </div>
      </div>

      {/* RIGHT PANEL: Inspector */}
      <div className="w-80 border-l border-border bg-card/50 flex flex-col shrink-0 hidden lg:flex">
        <div className="h-12 border-b border-border flex items-center px-4 font-medium text-sm">
          Inspector
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          <div className="space-y-2">
            <div className="text-xs font-semibold text-muted-foreground uppercase">Note Metadata</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-muted-foreground">Type</div><div>Basic</div>
              <div className="text-muted-foreground">Deck</div><div>Biology</div>
              <div className="text-muted-foreground">Created</div><div>Oct 24, 2024</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-xs font-semibold text-muted-foreground uppercase">FSRS Memory State</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-muted-foreground">Stability</div><div className="text-green-500">84.2%</div>
              <div className="text-muted-foreground">Difficulty</div><div>4.1</div>
              <div className="text-muted-foreground">Interval</div><div>21 days</div>
              <div className="text-muted-foreground">Lapses</div><div>0</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}