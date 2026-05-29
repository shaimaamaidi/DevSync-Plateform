import { useEffect, useRef, useState } from "react";
import { Check, Plus, X, Pencil } from "lucide-react";

interface EditableListProps {
  items: string[];
  onChange: (items: string[]) => void;
  accent?: "info" | "danger" | "success" | "amber";
}

const ACCENT_COLORS = {
  info:    { bg: "rgba(59,130,246,0.08)",  fg: "#3b82f6", dash: "rgba(59,130,246,0.3)" },
  danger:  { bg: "rgba(239,68,68,0.08)",   fg: "#ef4444", dash: "rgba(239,68,68,0.3)" },
  success: { bg: "rgba(34,197,94,0.08)",   fg: "#16a34a", dash: "rgba(34,197,94,0.3)" },
  amber:   { bg: "rgba(245,158,11,0.08)",  fg: "#d97706", dash: "rgba(245,158,11,0.3)" },
};

export function EditableList({ items, onChange, accent = "info" }: EditableListProps) {
  const [editingIdx, setEditingIdx]   = useState<number | null>(null);
  const [editVal,    setEditVal]       = useState("");
  const [editError,  setEditError]     = useState<string | null>(null);
  const [newVal,     setNewVal]        = useState("");
  const [newError,   setNewError]      = useState<string | null>(null);
  const [adding,     setAdding]        = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const newRef   = useRef<HTMLInputElement>(null);
  const colors = ACCENT_COLORS[accent];

  useEffect(() => { if (editingIdx !== null) inputRef.current?.focus(); }, [editingIdx]);
  useEffect(() => { if (adding) newRef.current?.focus(); }, [adding]);

  // ── Edit existing item ──────────────────────────────────────────────────
  const startEdit = (i: number) => {
    setEditingIdx(i);
    setEditVal(items[i]);
    setEditError(null);
  };

  const saveEdit = () => {
    if (!editVal.trim()) {
      // Revert to old value + show error
      setEditError(
        "Ce champ ne peut pas être vide. Cliquez sur le bouton de suppression pour le retirer."
      );
      setEditVal(items[editingIdx!]); // revert
      return;
    }
    onChange(items.map((it, i) => (i === editingIdx ? editVal.trim() : it)));
    setEditingIdx(null);
    setEditError(null);
  };

  const cancelEdit = () => {
    setEditingIdx(null);
    setEditVal("");
    setEditError(null);
  };

  // ── Delete item ─────────────────────────────────────────────────────────
  const deleteItem = (i: number) => {
    if (items.length === 1) {
      // Can't delete last element — show error on that row
      setEditingIdx(i);
      setEditVal(items[i]);
      setEditError("Impossible de supprimer le dernier élément. Cette liste ne peut pas être vide.");
      return;
    }
    onChange(items.filter((_, idx) => idx !== i));
  };

  // ── Add new item ────────────────────────────────────────────────────────
  const saveNew = () => {
    if (!newVal.trim()) {
      setNewError("Ce champ est requis.");
      return;
    }
    onChange([...items, newVal.trim()]);
    setNewVal("");
    setNewError(null);
    setAdding(false);
  };

  const cancelNew = () => {
    setAdding(false);
    setNewVal("");
    setNewError(null);
  };

  return (
    <div className="flex flex-col gap-[5px]">
      {items.map((item, i) => (
        <div key={i} className="flex flex-col">
          <div
            className="flex items-center gap-2 py-[7px] px-3 rounded-lg border"
            style={{ background: colors.bg, borderColor: colors.dash }}
          >
            {editingIdx === i ? (
              <>
                <input
                  ref={inputRef}
                  value={editVal}
                  onChange={(e) => { setEditVal(e.target.value); setEditError(null); }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") saveEdit();
                    if (e.key === "Escape") cancelEdit();
                  }}
                  className="flex-1 border-none bg-transparent text-[13px] font-[inherit] outline-none leading-relaxed"
                  style={{ color: colors.fg }}
                />
                <button
                  onClick={saveEdit}
                  className="bg-transparent border-none cursor-pointer p-1 flex items-center shrink-0 rounded-[5px] transition-opacity hover:opacity-80 text-green-600"
                >
                  <Check size={13} strokeWidth={2.5} />
                </button>
                <button
                  onClick={cancelEdit}
                  className="bg-transparent border-none cursor-pointer p-1 flex items-center shrink-0 rounded-[5px] transition-opacity hover:opacity-80 text-slate-400"
                >
                  <X size={12} strokeWidth={2.5} />
                </button>
              </>
            ) : (
              <>
                <span
                  className="flex-1 text-[13px] leading-relaxed"
                  style={{ color: colors.fg }}
                >
                  {item}
                </span>
                <button
                  onClick={() => startEdit(i)}
                  className="bg-transparent border-none cursor-pointer p-1 flex items-center shrink-0 rounded-[5px] transition-opacity hover:opacity-80 text-slate-400 opacity-50"
                >
                  <Pencil size={11} strokeWidth={2} />
                </button>
                <button
                  onClick={() => deleteItem(i)}
                  className="bg-transparent border-none cursor-pointer p-1 flex items-center shrink-0 rounded-[5px] transition-opacity hover:opacity-80 text-red-500"
                >
                  <X size={12} strokeWidth={2.5} />
                </button>
              </>
            )}
          </div>

          {/* Row-level error (edit / delete-last) */}
          {editingIdx === i && editError && (
            <div className="text-destructive text-xs mt-1 px-1">
              {editError}
            </div>
          )}
        </div>
      ))}

      {adding ? (
        <div className="flex flex-col">
          <div
            className="flex items-center gap-2 py-[7px] px-3 rounded-lg border border-dashed"
            style={{ borderColor: colors.dash, background: colors.bg }}
          >
            <input
              ref={newRef}
              value={newVal}
              onChange={(e) => { setNewVal(e.target.value); setNewError(null); }}
              onKeyDown={(e) => {
                if (e.key === "Enter") saveNew();
                if (e.key === "Escape") cancelNew();
              }}
              placeholder="Tapez et appuyez sur Entrée…"
              className="flex-1 border-none bg-transparent text-[13px] font-[inherit] outline-none leading-relaxed"
            />
            <button
              onClick={saveNew}
              className="bg-transparent border-none cursor-pointer p-1 flex items-center shrink-0 rounded-[5px] transition-opacity hover:opacity-80 text-green-600"
            >
              <Check size={13} strokeWidth={2.5} />
            </button>
            <button
              onClick={cancelNew}
              className="bg-transparent border-none cursor-pointer p-1 flex items-center shrink-0 rounded-[5px] transition-opacity hover:opacity-80 text-slate-400"
            >
              <X size={12} strokeWidth={2.5} />
            </button>
          </div>

          {/* New-item error */}
          {newError && (
            <div className="text-destructive text-xs mt-1 px-1">
              {newError}
            </div>
          )}
        </div>
      ) : (
        <button
          onClick={() => setAdding(true)}
          className="flex items-center gap-1.5 py-1.5 px-3 rounded-lg border border-dashed bg-transparent cursor-pointer text-[12px] font-[inherit] font-medium transition-opacity hover:opacity-75"
          style={{ borderColor: colors.dash, color: colors.fg }}
        >
          <Plus size={12} strokeWidth={2.5} /> Ajouter un élément
        </button>
      )}
    </div>
  );
}