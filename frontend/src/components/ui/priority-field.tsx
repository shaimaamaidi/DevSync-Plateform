import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, Loader2 } from 'lucide-react';
import type { FolderWithListsMetadata } from '@/api';

const DEFAULT_PRIORITIES = ['urgent', 'high', 'normal', 'low'];

const PRIORITY_DOT: Record<string, string> = {
  urgent: 'bg-red-500',
  high: 'bg-amber-500',
  medium: 'bg-blue-500',
  normal: 'bg-blue-500',
  low: 'bg-muted-foreground',
};

interface Props {
  value: string;
  onChange: (v: string) => void;
  priorities: string[];     
  disabled?: boolean;
  structureLoading: boolean;
  structure: FolderWithListsMetadata[];
}

export function PriorityField({ value, onChange, priorities, disabled, structureLoading, structure }: Props) {
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

  const allPriorities = priorities.length > 0 ? priorities : DEFAULT_PRIORITIES;

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        disabled={disabled}
        onClick={() => !disabled && setOpen(p => !p)}
        className={`w-full text-left text-sm border border-border rounded-md bg-background px-2 py-1 flex items-center gap-1.5 focus:outline-none focus:ring-2 focus:ring-ring min-h-[34px] ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        }`}
      >
        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${PRIORITY_DOT[value?.toLowerCase()] ?? 'bg-blue-500'}`} />
        <span className="flex-1 truncate capitalize">{value || <span className="text-muted-foreground">Priority…</span>}</span>
        <ChevronDown className="w-3.5 h-3.5 flex-shrink-0" />
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-popover border border-border rounded-md shadow-md">
          {isLoading ? (
            <div className="flex items-center justify-center gap-2 px-3 py-4 text-sm text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading…</span>
            </div>
          ) : (
            <>
            {allPriorities.map(p => (
              <button
                key={p}
                type="button"
                onClick={() => { onChange(p); setOpen(false); }}
                className="w-full text-left flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted transition-colors capitalize"
              >
                {value === p
                  ? <Check className="w-3.5 h-3.5 text-primary flex-shrink-0" />
                  : <span className="w-3.5 h-3.5 flex-shrink-0" />}
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${PRIORITY_DOT[p.toLowerCase()] ?? 'bg-blue-500'}`} />
                {p}
              </button>
            ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}