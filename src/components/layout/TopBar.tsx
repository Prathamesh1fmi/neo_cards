import React from "react";
import { Search, Sun, Moon, Laptop, Menu } from "lucide-react";
import { useTheme } from "@/components/theme/ThemeProvider";
import { KeyboardShortcut } from "@/components/ui/KeyboardShortcut";

export function TopBar({ toggleSidebar, sidebarOpen }: { toggleSidebar: () => void, sidebarOpen: boolean }) {
  const { theme, setTheme } = useTheme();

  return (
    <header className="h-14 border-b border-border bg-card/80 backdrop-blur-md flex items-center justify-between px-4 sticky top-0 z-10">
      <div className="flex items-center gap-4">
        {!sidebarOpen && (
          <button onClick={toggleSidebar} className="p-1.5 hover:bg-accent rounded-md text-muted-foreground">
            <Menu size={18} />
          </button>
        )}
        <div className="text-sm font-medium text-muted-foreground">Workspace / Dashboard</div>
      </div>

      <div className="flex items-center gap-2">
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-muted/50 border border-border/50 text-sm text-muted-foreground hover:bg-muted transition-colors w-64 justify-between">
          <div className="flex items-center gap-2">
            <Search size={14} />
            <span>Search or jump to...</span>
          </div>
          <KeyboardShortcut keys={['Ctrl', 'K']} />
        </button>

        <div className="flex items-center gap-1 border-l border-border pl-2 ml-2">
          <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} className="p-1.5 rounded-md hover:bg-muted text-muted-foreground"><Sun size={16} /></button>
          <button onClick={() => setTheme('dark')} className="p-1.5 rounded-md hover:bg-muted text-muted-foreground"><Moon size={16} /></button>
          <button onClick={() => setTheme('system')} className="p-1.5 rounded-md hover:bg-muted text-muted-foreground"><Laptop size={16} /></button>
        </div>
      </div>
    </header>
  );
}