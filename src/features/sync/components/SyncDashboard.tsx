import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import { Cloud, CloudOff, CloudUpload, CloudDownload, RefreshCw, Server, Shield, Database } from 'lucide-react';

export function SyncDashboard() {
  const [status, setStatus] = useState("idle");
  const [pending, setPending] = useState(0);
  const [lastSync, setLastSync] = useState("Never");

  useEffect(() => {
    // Initial load
    invoke('get_sync_status').then((res: any) => {
      setPending(res.pending_changes);
      if (res.last_sync) setLastSync(res.last_sync);
    });

    // Listen to background sync events emitted by Rust
    const unlisten = listen('sync_event', (event) => {
      setStatus(event.payload as string);
      if (event.payload === 'Completed') {
        setPending(0);
        setLastSync('Just now');
        setTimeout(() => setStatus('idle'), 2000);
      }
    });

    return () => { unlisten.then(f => f()); };
  }, []);

  const handleManualSync = async () => {
    if (status !== 'idle' && status !== 'Completed') return;
    try {
      await invoke('trigger_manual_sync');
    } catch (e) {
      console.error("Sync failed:", e);
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-background pt-8 pb-12 px-6 sm:px-12 max-w-4xl mx-auto overflow-y-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Synchronization</h1>
          <p className="text-sm text-muted-foreground mt-1">Manage local replication and cloud connections.</p>
        </div>
        <button 
          onClick={handleManualSync}
          disabled={status !== 'idle' && status !== 'Completed'}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
        >
          <RefreshCw size={14} className={status !== 'idle' && status !== 'Completed' ? 'animate-spin' : ''} />
          {status === 'idle' || status === 'Completed' ? 'Sync Now' : status}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
          <div className="text-muted-foreground mb-3 text-sm font-medium flex items-center gap-2"><Cloud size={16}/> Status</div>
          <div className="text-2xl font-semibold">{status === 'idle' ? 'Connected' : status}</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
          <div className="text-muted-foreground mb-3 text-sm font-medium flex items-center gap-2"><Database size={16}/> Unsynced Changes</div>
          <div className="text-2xl font-semibold">{pending}</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
          <div className="text-muted-foreground mb-3 text-sm font-medium flex items-center gap-2"><RefreshCw size={16}/> Last Sync</div>
          <div className="text-2xl font-semibold">{lastSync}</div>
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden mb-8">
        <div className="px-6 py-4 border-b border-border font-medium">Provider Configuration</div>
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase flex items-center gap-2 mb-2"><Server size={14}/> Transport Node</label>
              <input type="text" value="https://sync.neocards.io/v1" disabled className="w-full bg-muted/50 border border-border text-sm rounded-md px-3 py-2 cursor-not-allowed opacity-70" />
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase flex items-center gap-2 mb-2"><Shield size={14}/> E2E Encryption</label>
              <div className="flex items-center gap-2 bg-green-500/10 text-green-600 border border-green-500/20 px-3 py-2 rounded-md text-sm font-medium">
                <Shield size={16} /> Enabled (AES-256-GCM)
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-border font-medium">Change Journal Activity</div>
        <div className="p-0">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted/30 text-muted-foreground">
              <tr>
                <th className="px-6 py-3 font-medium">Entity</th>
                <th className="px-6 py-3 font-medium">Operation</th>
                <th className="px-6 py-3 font-medium">Timestamp</th>
                <th className="px-6 py-3 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {['Note', 'Card', 'DeckSettings'].map((entity, i) => (
                <tr key={i} className="hover:bg-accent/50">
                  <td className="px-6 py-3 font-medium">{entity}</td>
                  <td className="px-6 py-3"><span className="bg-blue-500/10 text-blue-500 px-2 py-0.5 rounded text-xs">Update</span></td>
                  <td className="px-6 py-3 text-muted-foreground">Oct 24, 14:0{i}</td>
                  <td className="px-6 py-3 text-right">
                    {i === 0 ? <span className="text-amber-500 flex items-center justify-end gap-1"><CloudUpload size={14}/> Pending</span> : <span className="text-green-500 flex items-center justify-end gap-1"><Cloud size={14}/> Synced</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}