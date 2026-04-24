import { RotateCcw, FlaskConical } from "lucide-react";

interface ChatHeaderProps {
  step: "idle" | "market_review" | "backlog_edit" | "finalizing" | "done";
  onReset: () => void;
}

const STEP_LABELS = {
  idle: "",
  market_review: "Market Review",
  backlog_edit: "Editing Backlog",
  finalizing: "Finalizing…",
  done: "Complete",
};

export function ChatHeader({ step, onReset }: ChatHeaderProps) {
  return (
    <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100 bg-white shrink-0">
      
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-[10px] bg-foreground flex items-center justify-center">
          <div className="grid grid-cols-2 gap-[3px] w-[18px]">
            <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-90" />
            <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-60" />
            <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-60" />
            <div className="w-[7px] h-[7px] rounded-[1.5px] bg-background opacity-30" />
          </div>
        </div>
        <div>
          <p className="text-[15px] font-bold text-slate-900 tracking-tight">
            Backlog Agent
          </p>

          <div className="flex items-center gap-1 mt-[2px]">
            <span className="w-[6px] h-[6px] rounded-full bg-green-500 animate-pulse" />
            <p className="text-[11px] text-slate-400">
              Market intelligence · Agile backlog generation
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {step !== "idle" && (
          <div className="flex items-center gap-1 px-3 py-[5px] rounded-full border border-slate-200 bg-slate-50 text-[11px] text-slate-500 font-medium">
            <FlaskConical size={11} strokeWidth={2} />
            <span>{STEP_LABELS[step]}</span>
          </div>
        )}

        <button
          onClick={onReset}
          className="flex items-center gap-1 px-3 py-[7px] rounded-lg border border-slate-200 text-slate-500 text-xs font-medium hover:bg-slate-50 hover:border-slate-300 transition"
        >
          <RotateCcw size={12} strokeWidth={2} />
          New chat
        </button>
      </div>
    </div>
  );
}