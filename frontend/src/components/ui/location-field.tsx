import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Plus, Loader2, List } from 'lucide-react';
import type { FolderWithListsMetadata } from '@/api/api';

const FOLDERLESS_MARKER = '__folderless__';

export interface LocationOption {
  listId: string;
  label: string;       // "FolderName / ListName" or "ListName"
  statuses: string[];
  priorities: string[];
}

export function buildLocationOptions(structure: FolderWithListsMetadata[]): LocationOption[] {
  const opts: LocationOption[] = [];
  for (const folder of structure) {
    const isFolderless =
      folder.name === FOLDERLESS_MARKER ||
      folder.id === (folder.lists?.[0]?.id ?? null);
    for (const list of folder.lists ?? []) {
      opts.push({
        listId: list.id,
        label: isFolderless
          ? list.name
          : `${folder.name} / ${list.name}`,
        statuses: list.statuses ?? [],
        priorities: list.priorities ?? [],
      });
    }
  }
  return opts;
}

interface Props {
  value: string;                     
  onChange: (label: string, statuses: string[], priorities: string[]) => void;
  structure: FolderWithListsMetadata[];
  structureLoading: boolean;
  spaceId: string;
  onRequestAddList: () => void;       
}

export function LocationField({
  value,
  onChange,
  structure,
  structureLoading,
  onRequestAddList,
}: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const [stale, setStale] = useState(false);
  const options = buildLocationOptions(structure);
  const isLoading = structureLoading || stale; 

  useEffect(() => {
    setStale(false);
  }, [structure]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSelect = (opt: LocationOption) => {
    onChange(opt.label, opt.statuses, opt.priorities);
    setOpen(false);
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(p => !p)}
        className="w-full text-left text-sm border border-border rounded-md bg-background px-2 py-1 flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-ring min-h-[34px]"
      >
        {value ? (
          <span className="truncate flex-1">{value}</span>
        ) : (
          <span className="text-muted-foreground flex-1">No location selected</span>
        )}
        <ChevronDown className="w-3.5 h-3.5 flex-shrink-0" />
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-popover border border-border rounded-md shadow-md max-h-52 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center gap-2 px-3 py-4 text-sm text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading…</span>
            </div>
          ) : (
            <>
              {options.length === 0 && (
                <div className="px-3 py-2 text-xs text-muted-foreground">
                  {structure.length > 0 ? 'no list available' : 'no folder and no list available'}
                </div>
              )}
              {options.map(opt => (
                <button
                  key={opt.listId}
                  type="button"
                  onClick={() => handleSelect(opt)}
                  className={`w-full text-left flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted transition-colors ${
                    value === opt.label ? 'bg-muted font-medium' : ''
                  }`}
                >
                  <List className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />
                  <span dir="ltr">{opt.label}</span>
                </button>
              ))}

              <div className="border-t border-border">
                <button
                  type="button"
                  onClick={() => {
                    setOpen(false);
                    onRequestAddList();
                  }}
                  className="w-full text-left flex items-center gap-2 px-3 py-2 text-sm text-primary hover:bg-primary/5 transition-colors font-medium"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Create new list…
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}