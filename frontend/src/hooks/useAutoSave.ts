import { useEffect, useRef, useState } from 'react';

interface UseAutoSaveOptions {
  key: string; // LocalStorage key
  data: any; // Data to save
  interval?: number; // Auto-save interval in milliseconds (default: 30000 = 30s)
  enabled?: boolean; // Enable/disable auto-save
}

interface UseAutoSaveReturn {
  savedData: any | null; // Retrieved saved data
  lastSaved: Date | null; // Last save timestamp
  clearSaved: () => void; // Clear saved data
  isSaving: boolean; // Currently saving
}

export function useAutoSave({
  key,
  data,
  interval = 30000, // 30 seconds default
  enabled = true
}: UseAutoSaveOptions): UseAutoSaveReturn {
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [savedData, setSavedData] = useState<any | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const previousDataRef = useRef<string>('');
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Load saved data on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(key);
      if (stored) {
        const parsed = JSON.parse(stored);
        setSavedData(parsed.data);
        setLastSaved(new Date(parsed.timestamp));
      }
    } catch (error) {
      console.error('Failed to load saved data:', error);
    }
  }, [key]);

  // Auto-save function
  const saveData = () => {
    if (!enabled || !data) return;

    const currentData = JSON.stringify(data);

    // Only save if data has changed
    if (currentData === previousDataRef.current) {
      return;
    }

    setIsSaving(true);

    try {
      const savePayload = {
        data,
        timestamp: new Date().toISOString()
      };

      localStorage.setItem(key, JSON.stringify(savePayload));
      previousDataRef.current = currentData;
      setLastSaved(new Date());
    } catch (error) {
      console.error('Failed to save data:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Clear saved data
  const clearSaved = () => {
    try {
      localStorage.removeItem(key);
      setSavedData(null);
      setLastSaved(null);
      previousDataRef.current = '';
    } catch (error) {
      console.error('Failed to clear saved data:', error);
    }
  };

  // Set up auto-save interval
  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Save immediately when data changes (debounced by interval)
    intervalRef.current = setInterval(() => {
      saveData();
    }, interval);

    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, data, interval]);

  // Save on unmount (if enabled)
  useEffect(() => {
    return () => {
      if (enabled && data) {
        saveData();
      }
    };
  }, []);

  return {
    savedData,
    lastSaved,
    clearSaved,
    isSaving
  };
}
