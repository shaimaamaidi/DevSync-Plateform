import { useEffect, useRef, useState } from "react";

interface EditableTextProps {
  value: string;
  onChange: (v: string) => void;
  editable: boolean;
  className?: string;
  placeholder?: string;
  multiline?: boolean;
}

export function EditableText({
  value,
  onChange,
  editable,
  className = "",
  placeholder = "…",
  multiline = false,
}: EditableTextProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const ref = useRef<HTMLInputElement & HTMLTextAreaElement>(null);

  useEffect(() => { setDraft(value); }, [value]);

  const commit = () => {
    const trimmed = draft.trim();
    if (trimmed) 
      onChange(trimmed);
    else 
      setDraft(value);
    setEditing(false);
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !multiline){ 
      e.preventDefault(); commit(); 
    }
    if (e.key === "Escape"){ 
      setDraft(value); setEditing(false); 
    }
  };

  if (!editable) {
    return <span className={className}>{value}</span>;
  }

  if (editing) {
    const shared = {
      ref,
      value: draft,
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
        setDraft(e.target.value),
      onBlur: commit,
      onKeyDown: onKey,
      placeholder,
      autoFocus: true,
      className: `${className} bg-white border border-slate-300 rounded-md px-1.5 outline-none focus:border-slate-500 resize-none w-full`,
    };
    return multiline
      ? <textarea rows={2} {...(shared as any)} />
      : <input type="text" {...(shared as any)} />;
  }

  return (
    <span
      className={`${className} cursor-text rounded hover:bg-slate-100 px-1 -mx-1 transition-colors inline-flex items-center min-h-[28px] sm:min-h-0`}
      onClick={() => { setDraft(value); setEditing(true); }}
      title="Click to edit"
    >
      {value || <span className="text-slate-300 italic">{placeholder}</span>}
    </span>
  );
}