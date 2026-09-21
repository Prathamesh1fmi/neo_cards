import React, { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import { X, Save, Settings2, Sliders, CalendarDays, BrainCircuit } from "lucide-react";

export interface DeckSettings {
  deck_id: string;
  new_cards_per_day: number;
  reviews_per_day: number;
}

export function DeckSettingsModal({ isOpen, onClose, deckId }: { isOpen: boolean, onClose: () => void, deckId: string }) {
  const [activeTab, setActiveTab] = useState("daily");
  const [settings, setSettings] = useState<DeckSettings>({
    deck_id: deckId,
    new_cards_per_day: 20,
    reviews_per_day: 200,
  });
  const [desiredRetention, setDesiredRetention] = useState(0.90);
  const [learningSteps, setLearningSteps] = useState("1m 10m");

  useEffect(() => {
    if (isOpen && deckId) {
      invoke("get_deck_settings", { deckId }).then((res: any) => {
        if (res) {
          setSettings(res);
        }
      }).catch(console.error);
    }
  }, [isOpen, deckId]);

  const handleSave = async () => {
    try {
      await invoke("update_deck_settings", { settings });
      onClose();
    } catch (e) {
      console.error(e);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-[800px] h-[600px] bg-card border border-border shadow-2xl rounded-xl flex overflow-hidden">
        
        {/* Left Tabs Sidebar */}
        <div className="w-56 bg-muted/30 border-r border-border flex flex-col p-2 space-y-1 select-none">
          <div className="px-3 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2">Deck Options</div>
          
          <button onClick={() => setActiveTab("daily")} className={`flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${activeTab === 'daily' ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-accent text-muted-foreground'}`}>
            <CalendarDays size={16} /> Daily Limits
          </button>
          
          <button onClick={() => setActiveTab("new")} className={`flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${activeTab === 'new' ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-accent text-muted-foreground'}`}>
            <Settings2 size={16} /> New Cards
          </button>

          <button onClick={() => setActiveTab("fsrs")} className={`flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${activeTab === 'fsrs' ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-accent text-muted-foreground'}`}>
            <BrainCircuit size={16} /> FSRS Algorithm
          </button>
        </div>

        {/* Right Content */}
        <div className="flex-1 flex flex-col bg-background">
          <div className="h-14 border-b border-border flex items-center justify-between px-6">
            <h2 className="text-lg font-semibold">Settings</h2>
            <button onClick={onClose} className="p-2 text-muted-foreground hover:bg-accent rounded-full"><X size={18} /></button>
          </div>

          <div className="flex-1 overflow-y-auto p-6">
            {activeTab === "daily" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold mb-4 text-muted-foreground uppercase">Daily Limits</h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-sm">New cards/day</div>
                        <div className="text-xs text-muted-foreground mt-0.5">Maximum number of new cards to introduce in a single day.</div>
                      </div>
                      <input 
                        type="number" 
                        value={settings.new_cards_per_day}
                        onChange={(e) => setSettings({...settings, new_cards_per_day: parseInt(e.target.value) || 0})}
                        className="w-20 bg-muted/50 border border-border px-2 py-1 text-sm rounded-md text-right focus:outline-none focus:ring-1 focus:ring-primary"
                      />
                    </div>
                    
                    <div className="w-full h-px bg-border"></div>

                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-sm">Maximum reviews/day</div>
                        <div className="text-xs text-muted-foreground mt-0.5">Cap the total number of reviews per day to prevent burnout.</div>
                      </div>
                      <input 
                        type="number" 
                        value={settings.reviews_per_day}
                        onChange={(e) => setSettings({...settings, reviews_per_day: parseInt(e.target.value) || 0})}
                        className="w-20 bg-muted/50 border border-border px-2 py-1 text-sm rounded-md text-right focus:outline-none focus:ring-1 focus:ring-primary"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "new" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold mb-4 text-muted-foreground uppercase">New Cards</h3>
                  <div className="space-y-4">
                    <div className="flex flex-col gap-2">
                      <div>
                        <div className="font-medium text-sm">Learning steps</div>
                        <div className="text-xs text-muted-foreground mt-0.5">Time delays (e.g., 1m 10m) before a card becomes a Review card. FSRS recommends short steps.</div>
                      </div>
                      <input 
                        type="text" 
                        value={learningSteps}
                        onChange={(e) => setLearningSteps(e.target.value)}
                        className="w-full bg-muted/50 border border-border px-3 py-2 text-sm rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "fsrs" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold mb-4 text-muted-foreground uppercase">FSRS Scheduler</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-sm">Desired Retention</div>
                        <div className="text-xs text-muted-foreground mt-0.5">0.80 to 0.95. A higher value means shorter intervals and more reviews. 0.90 is optimal.</div>
                      </div>
                      <input 
                        type="number" 
                        step="0.01"
                        min="0.70"
                        max="0.99"
                        value={desiredRetention}
                        onChange={(e) => setDesiredRetention(parseFloat(e.target.value) || 0.90)}
                        className="w-20 bg-muted/50 border border-border px-2 py-1 text-sm rounded-md text-right focus:outline-none focus:ring-1 focus:ring-primary"
                      />
                    </div>
                    
                    <div className="bg-primary/5 border border-primary/20 rounded-md p-4 mt-6">
                      <div className="flex items-center gap-2 text-primary font-medium text-sm mb-2">
                        <BrainCircuit size={16} /> FSRS Optimization
                      </div>
                      <div className="text-xs text-muted-foreground leading-relaxed mb-4">
                        FSRS requires at least 400 reviews to calculate custom machine learning weights for your memory. 
                        Do not manually edit these parameters.
                      </div>
                      <button className="px-4 py-2 bg-secondary text-secondary-foreground text-sm font-medium rounded hover:bg-secondary/80 border border-border transition-colors w-full">
                        Optimize FSRS Parameters
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-border bg-muted/10 flex justify-end gap-3">
            <button onClick={onClose} className="px-4 py-2 text-sm font-medium hover:bg-accent rounded-md border border-transparent transition-colors">
              Cancel
            </button>
            <button onClick={handleSave} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition-colors">
              <Save size={16} /> Save Options
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

