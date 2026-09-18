import React from "react";
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