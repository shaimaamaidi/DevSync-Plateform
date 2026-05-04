import { useState, useRef } from 'react';
import { ChevronDown, Check, X } from 'lucide-react';
import { useMembers } from '@/hooks/use-members';
import { UNASSIGNED } from './assignees-avatar';

export function AssigneeField({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  const { members, loading } = useMembers();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const selected =
    value === UNASSIGNED || !value
      ? []
      : value.split(',').map(s => s.trim());

  const toggle = (name: string) => {
    const next = selected.includes(name)
      ? selected.filter(n => n !== name)
      : [...selected, name];

    onChange(next.length ? next.join(', ') : UNASSIGNED);
  };

  const remove = (name: string) => {
    const next = selected.filter(n => n !== name);
    onChange(next.length ? next.join(', ') : UNASSIGNED);
  };

  // close outside click
  useState(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  });

  return (
    <div ref={ref} className="relative">
      <div
        onClick={() => setOpen(p => !p)}
        className="border border-border rounded-md px-2 py-1 min-h-[34px] flex flex-wrap gap-1 cursor-pointer"
      >
        {selected.length === 0 ? (
          <span className="text-muted-foreground">Unassigned</span>
        ) : (
          selected.map(name => (
            <span
              key={name}
              className="bg-primary/10 text-primary text-xs px-1.5 py-0.5 rounded-md flex items-center gap-1"
            >
              {name}
              <X
                className="w-3 h-3 cursor-pointer"
                onClick={e => {
                  e.stopPropagation();
                  remove(name);
                }}
              />
            </span>
          ))
        )}
        <ChevronDown className="ml-auto w-3.5 h-3.5" />
      </div>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border rounded-md shadow">
          {loading ? (
            <div className="p-2 text-xs">Loading...</div>
          ) : (
            members.map(m => {
              const name = m.arabic_name ?? '';
              const isSelected = selected.includes(name);

              return (
                <div
                  key={m.id}
                  onClick={() => toggle(name)}
                  className="flex items-center gap-2 px-3 py-2 cursor-pointer hover:bg-muted"
                >
                  <div
                    className={`w-4 h-4 border flex items-center justify-center ${
                      isSelected ? 'bg-primary' : ''
                    }`}
                  >
                    {isSelected && <Check className="w-3 h-3" />}
                  </div>
                  <span dir="rtl">{name}</span>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}