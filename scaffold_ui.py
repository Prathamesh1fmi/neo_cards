import os
from pathlib import Path

base = Path('.')

dirs = [
    'src/pages',
    'src/components/layout',
    'src/components/ui',
    'src/components/theme',
    'src/router'
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

ui_files = {}

# 1. Navigation Shell
ui_files['src/components/layout/NavigationShell.tsx'] = '''import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { StatusBar } from "./StatusBar";
import { CommandPalette } from "./CommandPalette";

export function NavigationShell() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
      <Sidebar isOpen={sidebarOpen} toggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex flex-1 flex-col overflow-hidden relative">
        <TopBar toggleSidebar={() => setSidebarOpen(!sidebarOpen)} sidebarOpen={sidebarOpen} />
        <main className="flex-1 overflow-auto bg-muted/20 relative">
          <Outlet />
        </main>
        <StatusBar />
      </div>
      <CommandPalette />
    </div>
  );
}
'''

# 2. Sidebar
ui_files['src/components/layout/Sidebar.tsx'] = '''import React from "react";
import { NavLink } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { BookOpen, Home, Search, Settings, PieChart, Layers, Blocks, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isOpen: boolean;
  toggle: () => void;
}

export function Sidebar({ isOpen, toggle }: SidebarProps) {
  const links = [
    { name: "Dashboard", to: "/", icon: Home },
    { name: "Decks", to: "/decks", icon: Layers },
    { name: "Review", to: "/review", icon: BookOpen },
    { name: "Browse", to: "/browse", icon: Search },
    { name: "Statistics", to: "/stats", icon: PieChart },
    { name: "Plugins", to: "/plugins", icon: Blocks },
  ];

  return (
    <motion.aside
      initial={{ width: 256 }}
      animate={{ width: isOpen ? 256 : 64 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="h-full border-r border-border bg-card flex flex-col relative shrink-0 z-20"
    >
      <div className="h-14 flex items-center px-4 border-b border-border justify-between">
        <AnimatePresence>
          {isOpen && (
            <motion.span 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              exit={{ opacity: 0 }}
              className="font-semibold text-sm tracking-tight truncate"
            >
              NeoCards
            </motion.span>
          )}
        </AnimatePresence>
        <button onClick={toggle} className="p-1 hover:bg-accent rounded-md text-muted-foreground transition-colors">
          {isOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-4 flex flex-col gap-1 px-2">
        <div className="px-2 pb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {isOpen ? "Menu" : "•••"}
        </div>
        {links.map((link) => (
          <NavLink
            key={link.name}
            to={link.to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-2 py-2 rounded-md transition-colors text-sm font-medium",
                isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )
            }
            title={!isOpen ? link.name : undefined}
          >
            <link.icon size={18} className="shrink-0" />
            <AnimatePresence>
              {isOpen && (
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, width: 0 }}
                  className="truncate"
                >
                  {link.name}
                </motion.span>
              )}
            </AnimatePresence>
          </NavLink>
        ))}
      </div>

      <div className="p-2 border-t border-border">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 px-2 py-2 rounded-md transition-colors text-sm font-medium",
              isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-accent hover:text-foreground"
            )
          }
        >
          <Settings size={18} className="shrink-0" />
          {isOpen && <span>Settings</span>}
        </NavLink>
      </div>
    </motion.aside>
  );
}
'''

# 3. TopBar
ui_files['src/components/layout/TopBar.tsx'] = '''import React from "react";
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
          <button onClick={() => setTheme('light')} className={p-1.5 rounded-md }><Sun size={16} /></button>
          <button onClick={() => setTheme('dark')} className={p-1.5 rounded-md }><Moon size={16} /></button>
          <button onClick={() => setTheme('system')} className={p-1.5 rounded-md }><Laptop size={16} /></button>
        </div>
      </div>
    </header>
  );
}
'''

# 4. StatusBar
ui_files['src/components/layout/StatusBar.tsx'] = '''import React from "react";
import { Database, CheckCircle2 } from "lucide-react";

export function StatusBar() {
  return (
    <footer className="h-8 border-t border-border bg-card flex items-center px-4 justify-between text-xs text-muted-foreground z-10">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1">
          <CheckCircle2 size={12} className="text-green-500" />
          <span>All systems operational</span>
        </div>
        <div className="flex items-center gap-1">
          <Database size={12} />
          <span>Local SQLite</span>
        </div>
      </div>
      <div>NeoCards v0.1.0</div>
    </footer>
  );
}
'''

# 5. CommandPalette
ui_files['src/components/layout/CommandPalette.tsx'] = '''import React, { useEffect, useState } from "react";
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
'''

# 6. PageContainer
ui_files['src/components/layout/PageContainer.tsx'] = '''import React from "react";
import { motion } from "framer-motion";

export function PageContainer({ children, title }: { children: React.ReactNode, title?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className="p-6 max-w-6xl mx-auto w-full"
    >
      {title && <h1 className="text-3xl font-bold tracking-tight mb-6 text-foreground">{title}</h1>}
      {children}
    </motion.div>
  );
}
'''

# 7. UI Components
ui_files['src/components/ui/EmptyState.tsx'] = '''import React from "react";
import { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] border border-dashed border-border rounded-xl bg-card/50 text-center p-8">
      <div className="h-16 w-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mb-4">
        <Icon size={32} strokeWidth={1.5} />
      </div>
      <h3 className="text-lg font-semibold mb-1 text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-sm mb-6">{description}</p>
      {action}
    </div>
  );
}
'''

ui_files['src/components/ui/KeyboardShortcut.tsx'] = '''import React from "react";

export function KeyboardShortcut({ keys }: { keys: string[] }) {
  return (
    <div className="flex items-center gap-1">
      {keys.map((key, i) => (
        <kbd key={i} className="inline-flex h-5 items-center justify-center rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground uppercase">
          {key}
        </kbd>
      ))}
    </div>
  );
}
'''

# 8. Pages
pages = ['Dashboard', 'Decks', 'Review', 'Browse', 'Stats', 'Plugins', 'Settings']
from textwrap import dedent

for p in pages:
    ui_files[f'src/pages/{p}.tsx'] = dedent(f'''
    import React from "react";
    import {{ PageContainer }} from "@/components/layout/PageContainer";
    import {{ EmptyState }} from "@/components/ui/EmptyState";
    import {{ Layers }} from "lucide-react";

    export function {p}() {{
      return (
        <PageContainer title="{p}">
          <EmptyState 
            icon={{Layers}}
            title="Welcome to {p}"
            description="This is a premium placeholder. The business logic for this module will be implemented in future milestones."
            action={{
              <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition-colors">
                Simulate Action
              </button>
            }}
          />
        </PageContainer>
      );
    }}
    ''')

# 9. Router Setup
ui_files['src/router/index.tsx'] = '''import React from "react";
import { createBrowserRouter } from "react-router-dom";
import { NavigationShell } from "@/components/layout/NavigationShell";
import { Dashboard } from "@/pages/Dashboard";
import { Decks } from "@/pages/Decks";
import { Review } from "@/pages/Review";
import { Browse } from "@/pages/Browse";
import { Stats } from "@/pages/Stats";
import { Settings } from "@/pages/Settings";
import { Plugins } from "@/pages/Plugins";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <NavigationShell />,
    children: [
      { path: "/", element: <Dashboard /> },
      { path: "/decks", element: <Decks /> },
      { path: "/review", element: <Review /> },
      { path: "/browse", element: <Browse /> },
      { path: "/stats", element: <Stats /> },
      { path: "/settings", element: <Settings /> },
      { path: "/plugins", element: <Plugins /> },
    ]
  }
]);
'''

for filepath, content in ui_files.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("UI scaffolding complete.")
