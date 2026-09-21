import React, { useState } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { useTheme } from "@/components/theme/ThemeProvider";
import { Settings as SettingsIcon, Monitor, Cloud, Database, Palette, Save } from "lucide-react";

export function Settings() {
  const { theme, setTheme } = useTheme();
  const [activeTab, setActiveTab] = useState("appearance");

  return (
    <PageContainer title="Workspace / Settings">
      <div className="flex h-full bg-card border border-border rounded-xl overflow-hidden">
        
        {/* Left Sidebar Menu */}
        <div className="w-64 bg-muted/20 border-r border-border flex flex-col p-4 space-y-1">
          <button 
            onClick={() => setActiveTab("appearance")} 
            className={`flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${activeTab === 'appearance' ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-accent text-muted-foreground'}`}
          >
            <Palette size={16} /> Appearance
          </button>
          
          <button 
            onClick={() => setActiveTab("sync")} 
            className={`flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${activeTab === 'sync' ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-accent text-muted-foreground'}`}
          >
            <Cloud size={16} /> Cloud Sync
          </button>
          
          <button 
            onClick={() => setActiveTab("database")} 
            className={`flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${activeTab === 'database' ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-accent text-muted-foreground'}`}
          >
            <Database size={16} /> Database & Backups
          </button>
        </div>

        {/* Right Content */}
        <div className="flex-1 overflow-y-auto p-8 bg-background">
          <div className="max-w-2xl mx-auto space-y-8">
            
            {activeTab === "appearance" && (
              <div className="space-y-6">
                <div className="flex items-center gap-2 mb-6 border-b border-border pb-4">
                  <Palette className="text-primary" size={20} />
                  <h2 className="text-xl font-semibold">Appearance</h2>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">Theme Preference</div>
                      <div className="text-sm text-muted-foreground">Select how the application looks.</div>
                    </div>
                    <select 
                      value={theme} 
                      onChange={(e) => setTheme(e.target.value as any)}
                      className="bg-card border border-border rounded-md px-3 py-1.5 text-sm outline-none focus:ring-1 focus:ring-primary"
                    >
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                      <option value="system">System Default</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "sync" && (
              <div className="space-y-6">
                <div className="flex items-center gap-2 mb-6 border-b border-border pb-4">
                  <Cloud className="text-primary" size={20} />
                  <h2 className="text-xl font-semibold">Cloud Sync (NeoWeb)</h2>
                </div>
                
                <div className="space-y-4">
                  <div className="bg-primary/5 border border-primary/20 rounded-md p-4">
                    <h3 className="font-medium text-primary mb-1">NeoCards Cloud is disconnected</h3>
                    <p className="text-sm text-muted-foreground mb-4">Log in to sync your decks, reviews, and media across all your devices.</p>
                    <div className="flex gap-2">
                      <input type="text" placeholder="Email" className="flex-1 bg-background border border-border rounded-md px-3 py-1.5 text-sm outline-none focus:ring-1 focus:ring-primary" />
                      <input type="password" placeholder="Password" className="flex-1 bg-background border border-border rounded-md px-3 py-1.5 text-sm outline-none focus:ring-1 focus:ring-primary" />
                      <button className="px-4 py-1.5 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition-colors">Log In</button>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mt-6">
                    <div>
                      <div className="font-medium">Auto-sync on close</div>
                      <div className="text-sm text-muted-foreground">Automatically upload changes when you exit the app.</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "database" && (
              <div className="space-y-6">
                <div className="flex items-center gap-2 mb-6 border-b border-border pb-4">
                  <Database className="text-primary" size={20} />
                  <h2 className="text-xl font-semibold">Database & Backups</h2>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">Check Database</div>
                      <div className="text-sm text-muted-foreground">Verify database integrity and rebuild indices.</div>
                    </div>
                    <button className="px-4 py-1.5 bg-secondary text-secondary-foreground rounded-md text-sm font-medium hover:bg-secondary/80 border border-border transition-colors">
                      Run Check
                    </button>
                  </div>
                  
                  <div className="w-full h-px bg-border my-2"></div>

                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">Automatic Backups</div>
                      <div className="text-sm text-muted-foreground">Keep local snapshot copies of your SQLite database.</div>
                    </div>
                    <select className="bg-card border border-border rounded-md px-3 py-1.5 text-sm outline-none focus:ring-1 focus:ring-primary">
                      <option value="10">Keep 10 backups</option>
                      <option value="30">Keep 30 backups</option>
                      <option value="50">Keep 50 backups</option>
                      <option value="0">Disabled</option>
                    </select>
                  </div>
                  
                  <div className="w-full h-px bg-border my-2"></div>

                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">Force Full Sync</div>
                      <div className="text-sm text-muted-foreground text-destructive">Overwrite all cloud data with local data. Use with caution.</div>
                    </div>
                    <button className="px-4 py-1.5 bg-destructive/10 text-destructive rounded-md text-sm font-medium hover:bg-destructive/20 transition-colors border border-destructive/20">
                      Upload to NeoWeb
                    </button>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>

      </div>
    </PageContainer>
  );
}