import React, { useEffect, useState } from "react";
import { appWindow } from "@tauri-apps/api/window";
import { Minus, Square, X, Maximize2 } from "lucide-react";

export function TitleBar() {
  const [isMaximized, setIsMaximized] = useState(false);

  useEffect(() => {
    const unlisten = appWindow.onResized(() => {
      appWindow.isMaximized().then(setIsMaximized);
    });
    return () => {
      unlisten.then((f) => f());
    };
  }, []);

  return (
    <div
      data-tauri-drag-region
      className="h-10 bg-card border-b border-border flex items-center justify-between select-none fixed top-0 left-0 right-0 z-50"
    >
      <div className="flex items-center pl-4 gap-2" data-tauri-drag-region>
        <div className="w-3 h-3 rounded-full bg-primary/20"></div>
        <span className="text-xs font-semibold text-muted-foreground" data-tauri-drag-region>
          NeoCards
        </span>
      </div>

      <div className="flex h-full">
        <div
          className="inline-flex justify-center items-center w-12 h-full hover:bg-accent text-muted-foreground transition-colors cursor-default"
          onClick={() => appWindow.minimize()}
        >
          <Minus size={14} />
        </div>
        <div
          className="inline-flex justify-center items-center w-12 h-full hover:bg-accent text-muted-foreground transition-colors cursor-default"
          onClick={() => appWindow.toggleMaximize()}
        >
          {isMaximized ? <Maximize2 size={12} /> : <Square size={12} />}
        </div>
        <div
          className="inline-flex justify-center items-center w-12 h-full hover:bg-destructive hover:text-destructive-foreground text-muted-foreground transition-colors cursor-default"
          onClick={() => appWindow.close()}
        >
          <X size={16} />
        </div>
      </div>
    </div>
  );
}

