import React from "react";
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