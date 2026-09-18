import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import { FileUp, CheckCircle, AlertCircle } from 'lucide-react';

export function ImportDialog({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [filePath, setFilePath] = useState("");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<'idle' | 'importing' | 'success' | 'error'>('idle');

  useEffect(() => {
    const unlisten = listen('import_progress', (event: any) => {
      const { current, total, message } = event.payload;
      setProgress((current / total) * 100);
      setMessage(message);
    });
    return () => { unlisten.then(f => f()); };
  }, []);

  const handleImport = async () => {
    setStatus('importing');
    try {
      const result = await invoke('start_import', { 
        req: { file_path: filePath, format: 'csv', resolution: 'merge' } 
      });
      setMessage(result as string);
      setStatus('success');
    } catch (err: any) {
      setMessage(err);
      setStatus('error');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div className="w-[500px] bg-card border border-border shadow-2xl rounded-xl overflow-hidden flex flex-col">
        <div className="h-12 border-b border-border flex items-center px-4 font-medium">
          <FileUp size={16} className="mr-2 text-muted-foreground" /> Import Data
        </div>
        
        <div className="p-6 space-y-4 flex-1">
          {status === 'idle' && (
            <>
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase">File Path</label>
                <div className="flex gap-2 mt-1">
                  <div className="flex-1 border border-border bg-muted/50 px-3 py-2 text-sm rounded-md truncate text-muted-foreground select-none cursor-default">
                    {filePath || "No file selected"}
                  </div>
                  <button 
                    onClick={async () => {
                      const { open } = await import('@tauri-apps/api/dialog');
                      const selected = await open({ filters: [{ name: 'Data', extensions: ['csv', 'apkg', 'json'] }] });
                      if (selected) setFilePath(selected as string);
                    }}
                    className="px-4 py-2 bg-secondary text-secondary-foreground text-sm font-medium rounded-md hover:bg-secondary/80 border border-border transition-colors"
                  >
                    Browse...
                  </button>
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase">Conflict Resolution</label>
                <select className="w-full mt-1 border border-border bg-background px-3 py-2 text-sm rounded-md">
                  <option value="merge">Merge & Update Existing</option>
                  <option value="replace">Replace Existing</option>
                  <option value="skip">Skip Duplicates</option>
                </select>
              </div>
            </>
          )}

          {status === 'importing' && (
            <div className="py-8 text-center space-y-4">
              <div className="text-sm font-medium">{message}</div>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-primary transition-all duration-300" style={{ width: `${progress}%` }}></div>
              </div>
            </div>
          )}

          {status === 'success' && (
            <div className="py-8 text-center space-y-2">
              <CheckCircle size={48} className="mx-auto text-green-500" />
              <div className="font-semibold text-lg">Import Successful</div>
              <div className="text-sm text-muted-foreground">{message}</div>
            </div>
          )}

          {status === 'error' && (
            <div className="py-8 text-center space-y-2">
              <AlertCircle size={48} className="mx-auto text-destructive" />
              <div className="font-semibold text-lg text-destructive">Import Failed</div>
              <div className="text-sm text-muted-foreground">{message}</div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-border bg-muted/20 flex justify-end gap-2">
          {status !== 'importing' && (
            <button onClick={onClose} className="px-4 py-2 border border-border rounded-md text-sm hover:bg-accent font-medium">
              {status === 'success' || status === 'error' ? 'Close' : 'Cancel'}
            </button>
          )}
          {status === 'idle' && (
            <button onClick={handleImport} className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm hover:bg-primary/90 font-medium">
              Start Import
            </button>
          )}
        </div>
      </div>
    </div>
  );
}