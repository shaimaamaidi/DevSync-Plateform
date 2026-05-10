import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Plus, Check, Loader2 } from 'lucide-react';
import type { FolderWithListsMetadata } from '@/api';

interface Props {
  value: string;
  onChange: (v: string) => void;
  statuses: string[];          
  disabled?: boolean;
  structureLoading: boolean;
  structure: FolderWithListsMetadata[];
  onRequestAddStatus: () => void;
}

export function StatusField({ value, onChange, statuses, disabled, structureLoading, structure, onRequestAddStatus }: Props) {
  const [open, setOpen] = useState(false);
  const [stale, setStale] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const isLoading = structureLoading || stale; 

  useEffect(() => {
    setStale(false);
  }, [structure]);


  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const allStatuses = statuses.length > 0 ? statuses : ['To Do', 'In Progress', 'In Review', 'Done'];

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        disabled={disabled}
        onClick={() => !disabled && setOpen(p => !p)}
        className={`w-full text-left text-sm border border-border rounded-md bg-background px-2 py-1 flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-ring min-h-[34px] ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        }`}
      >
        <span className="flex-1 truncate">{value || <span className="text-muted-foreground">Status…</span>}</span>
        <ChevronDown className="w-3.5 h-3.5 flex-shrink-0" />
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-popover border border-border rounded-md shadow-md max-h-48 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center gap-2 px-3 py-4 text-sm text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading…</span>
            </div>
          ) : (
            <>
            {allStatuses.map(s => (
              <button
                key={s}
                type="button"
                onClick={() => { onChange(s); setOpen(false); }}
                className="w-full text-left flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted transition-colors"
              >
                {value === s && <Check className="w-3.5 h-3.5 text-primary flex-shrink-0" />}
                {value !== s && <span className="w-3.5 h-3.5 flex-shrink-0" />}
                {s}
              </button>
            ))}
            </>
          )}
          <div className="border-t border-border">
            <button
              type="button"
              onClick={() => { setOpen(false); onRequestAddStatus(); }}
              className="w-full text-left flex items-center gap-2 px-3 py-2 text-sm text-primary hover:bg-primary/5 transition-colors font-medium"
            >
              <Plus className="w-3.5 h-3.5" />
              Add status…
            </button>
          </div>
        </div>
      )}
    </div>
  );
}