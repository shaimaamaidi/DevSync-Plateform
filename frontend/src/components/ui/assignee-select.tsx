import type { MemberDTO } from "@/api/api";
import { Check, ChevronsUpDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface AssigneeSelectProps {
  value: string[];
  onChange: (mails: string[]) => void;
  members: MemberDTO[];
  loading: boolean;
  disabled?: boolean;
}

export function AssigneeSelect({
  value,
  onChange,
  members,
  loading,
  disabled,
}: AssigneeSelectProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node))
        setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const toggle = (mail: string) =>
    onChange(
      value.includes(mail) ? value.filter((m) => m !== mail) : [...value, mail],
    );

  const label =
    value.length === 0
      ? 'Select assignees…'
      : value.length === 1
      ? value[0]
      : `${value.length} assignees selected`;

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        disabled={disabled || loading}
        onClick={() => setOpen((p) => !p)}
        className="w-full flex items-center justify-between gap-2 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span className={value.length === 0 ? 'text-muted-foreground' : 'text-foreground'}>
          {loading ? 'Loading members…' : label}
        </span>
        <ChevronsUpDown className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />
      </button>

      {open && !loading && (
        <div className="absolute z-50 mt-1 left-0 w-full bg-popover border border-border rounded-md shadow-md max-h-48 overflow-y-auto">
          {members.length === 0 ? (
            <div className="px-3 py-2 text-xs text-muted-foreground italic">
              No members found
            </div>
          ) : (
            members.map((m) => {
              const mail = m.mail ?? '';
              if (!mail) return null;
              const selected = value.includes(mail);
              return (
                <button
                  key={m.id ?? mail}
                  type="button"
                  onClick={() => toggle(mail)}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted transition-colors text-left"
                >
                  <span
                    className={`w-4 h-4 flex-shrink-0 rounded border flex items-center justify-center transition-colors ${
                      selected
                        ? 'bg-primary border-primary text-primary-foreground'
                        : 'border-border'
                    }`}
                  >
                    {selected && <Check className="w-3 h-3" />}
                  </span>
                  <div className="flex flex-col min-w-0">
                    <span className="text-xs font-medium truncate">
                      {m.username ?? m.arabic_name ?? mail}
                    </span>
                    <span className="text-xs text-muted-foreground truncate">{mail}</span>
                  </div>
                </button>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
