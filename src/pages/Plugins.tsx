import React, { useState } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Puzzle, Download, Trash2, Power, Search, Settings2 } from "lucide-react";

export function Plugins() {
  const [plugins] = useState([
    { id: "1", name: "Image Occlusion Enhanced", author: "Glutanimate", version: "1.4.0", enabled: true, description: "Create flashcards from images by hiding parts of them." },
    { id: "2", name: "Heatmap Review", author: "NeoCards Community", version: "2.1.1", enabled: true, description: "Adds a GitHub-style review heatmap to your dashboard." },
    { id: "3", name: "AwesomeTTS", author: "AwesomeTTS Team", version: "1.23.0", enabled: false, description: "Add text-to-speech audio to your flashcards automatically." },
  ]);

  return (
    <PageContainer title="Workspace / Add-ons">
      <div className="flex flex-col h-full bg-card border border-border rounded-xl overflow-hidden">
        
        {/* Toolbar */}
        <div className="h-14 border-b border-border bg-muted/20 flex items-center justify-between px-4">
          <div className="relative w-64">
            <Search size={14} className="absolute left-2.5 top-2.5 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search installed add-ons..." 
              className="w-full bg-background border border-border rounded-md pl-8 pr-3 py-1.5 text-sm outline-none focus:ring-1 focus:ring-primary" 
            />
          </div>
          
          <button className="flex items-center gap-2 px-4 py-1.5 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition-colors">
            <Download size={16} /> Get Add-ons...
          </button>
        </div>

        {/* Plugin List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {plugins.map(plugin => (
            <div key={plugin.id} className={`flex items-center justify-between p-4 border rounded-lg transition-colors ${plugin.enabled ? 'bg-background border-border' : 'bg-muted/10 border-border/50'}`}>
              
              <div className="flex items-start gap-4">
                <div className={`mt-1 p-2 rounded-md ${plugin.enabled ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'}`}>
                  <Puzzle size={20} />
                </div>
                
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className={`font-semibold ${!plugin.enabled && 'text-muted-foreground'}`}>{plugin.name}</h3>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground font-medium">v{plugin.version}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1 max-w-xl">{plugin.description}</p>
                  <p className="text-xs text-muted-foreground mt-2 font-medium">By {plugin.author}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button 
                  className={`p-2 rounded-md transition-colors ${plugin.enabled ? 'text-primary hover:bg-primary/10' : 'text-muted-foreground hover:bg-accent'}`}
                  title={plugin.enabled ? "Disable add-on" : "Enable add-on"}
                >
                  <Power size={18} />
                </button>
                <button className="p-2 text-muted-foreground hover:bg-accent rounded-md" title="Configure add-on">
                  <Settings2 size={18} />
                </button>
                <button className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md" title="Uninstall add-on">
                  <Trash2 size={18} />
                </button>
              </div>

            </div>
          ))}

          <div className="mt-8 text-center bg-muted/20 border border-border border-dashed rounded-lg p-8">
            <Puzzle size={32} className="mx-auto text-muted-foreground mb-4" />
            <h3 className="font-semibold mb-2">Build your own Add-ons</h3>
            <p className="text-sm text-muted-foreground max-w-md mx-auto mb-4">
              NeoCards add-ons are built using standard web technologies (HTML, CSS, JS) and can interact directly with the SQLite database via our IPC bridge.
            </p>
            <button className="text-sm text-primary font-medium hover:underline">
              Read Developer Documentation &rarr;
            </button>
          </div>

        </div>
      </div>
    </PageContainer>
  );
}