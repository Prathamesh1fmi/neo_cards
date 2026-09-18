import React from "react";

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