import React, { useRef, useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

export function VirtualizedGrid({ query }: { query: string }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    invoke('search_cards', { query }).then((res: any) => {
      setRows(res);
    }).catch(console.error);
  }, [query]);

  return (
    <div ref={scrollRef} className="h-full w-full overflow-auto relative">
      <table className="w-full text-left border-collapse text-sm whitespace-nowrap">
        <thead className="sticky top-0 bg-card z-10 shadow-sm">
          <tr>
            <th className="font-semibold p-3 border-b border-r border-border w-10 text-center"><input type="checkbox"/></th>
            <th className="font-semibold p-3 border-b border-r border-border">Sort Field</th>
            <th className="font-semibold p-3 border-b border-r border-border">Deck</th>
            <th className="font-semibold p-3 border-b border-r border-border">Due Date</th>
            <th className="font-semibold p-3 border-b border-border">State</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.card_id} className="hover:bg-accent/50 cursor-pointer border-b border-border transition-colors group">
              <td className="p-3 border-r border-border text-center"><input type="checkbox" className="opacity-0 group-hover:opacity-100" /></td>
              <td className="p-3 border-r border-border truncate max-w-xs">{row.front}</td>
              <td className="p-3 border-r border-border">{row.deck}</td>
              <td className="p-3 border-r border-border text-muted-foreground">{row.due}</td>
              <td className="p-3">
                <span className="px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 text-xs font-medium">{row.state}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}