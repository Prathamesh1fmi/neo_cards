import { useEffect, useRef, useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

export function useAutosave(data: any, saveFn: (data: any) => Promise<any>, delay = 2000) {
  const [status, setStatus] = useState<'saved' | 'saving' | 'error' | 'unsaved'>('saved');
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    setStatus('unsaved');

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(async () => {
      setStatus('saving');
      try {
        await saveFn(data);
        setStatus('saved');
      } catch (err) {
        console.error("Autosave failed:", err);
        setStatus('error');
      }
    }, delay);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [data, delay, saveFn]);

  return status;
}