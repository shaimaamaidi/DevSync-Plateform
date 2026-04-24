import { useRef, useState } from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
  placeholder: string;
}

export function ChatInput({
  value,
  onChange,
  onSend,
  disabled,
  placeholder,
}: ChatInputProps) {
  const [rows, setRows] = useState(1);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);

    const textarea = e.target;
    setRows(Math.min(Math.max(1, textarea.scrollHeight / 24), 10));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && value.trim()) onSend();
    }
  };

  const canSend = value.trim() && !disabled;

  return (
    <div className="border-t border-slate-100 px-4 pt-3 pb-4 bg-white shrink-0">
      
      <div
        className="
          flex items-end gap-2
          bg-slate-50
          border border-slate-200
          rounded-xl
          px-3 py-2
          transition
          focus-within:border-slate-400
          focus-within:shadow-[0_0_0_3px_rgba(148,163,184,0.12)]
        "
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={rows}
          className="
            flex-1 resize-none bg-transparent
            text-[13px] text-slate-800
            leading-6 outline-none
            max-h-[120px] overflow-y-auto
            placeholder:text-slate-400
            disabled:opacity-50
          "
        />

        <button
          onClick={onSend}
          disabled={!canSend}
          className={`
            w-9 h-9 rounded-lg flex items-center justify-center
            transition transform
            ${canSend ? "bg-slate-900 hover:scale-105 active:scale-95" : "bg-slate-200 cursor-default opacity-30"}
          `}
        >
          <Send
            size={14}
            strokeWidth={2}
            className={canSend ? "text-white" : "text-slate-400"}
          />
        </button>
      </div>

      <p className="mt-1 ml-0.5 text-[10px] text-slate-300">
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}