import { RotateCcw, FlaskConical } from "lucide-react";
import logo from '@/assets/rido-logo.jpeg';

interface ChatHeaderProps {
  step: "idle" | "clarifying" | "market_review" | "backlog_edit" | "finalizing" | "done";
  clarifyingMode?: "clarification" | "conflicts"; 
  onReset: () => void;
}

const STEP_LABELS: Record<string, string> = {
  idle: "",
  clarifying_clarification: "Clarification",
  clarifying_conflicts: "Conflicts",
  market_review: "Market Review",
  backlog_edit: "Editing Backlog",
  finalizing: "Finalizing…",
  done: "Complete",
};

export function ChatHeader({ step, clarifyingMode, onReset }: ChatHeaderProps) {
  const labelKey =
    step === "clarifying" && clarifyingMode
      ? `clarifying_${clarifyingMode}`
      : step;

  return (
    <div className="flex items-center justify-between px-3 sm:px-5 py-3 border-b border-slate-100 bg-white shrink-0 gap-2">
      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
        <img
          src={logo}
          alt="Logo"
          className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl object-cover border border-border shrink-0"
        />
        <div className="min-w-0">
          <p className="text-[14px] sm:text-[15px] font-bold text-slate-900 tracking-tight truncate">
            Backlog Agent
          </p>
          <div className="flex items-center gap-1 mt-[2px]">
            <span className="w-[6px] h-[6px] rounded-full bg-green-500 animate-pulse shrink-0" />
            <p className="text-[10px] sm:text-[11px] text-slate-400 truncate">
              <span className="hidden sm:inline">Agile backlog generation</span>
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
        {step !== "idle" && STEP_LABELS[labelKey] && (
          <div className="flex items-center gap-1 px-2 sm:px-3 py-[5px] rounded-full border border-slate-200 bg-slate-50 text-[10px] sm:text-[11px] text-slate-500 font-medium">
            <FlaskConical size={11} strokeWidth={2} />
            <span className="hidden xs:inline">{STEP_LABELS[labelKey]}</span>
          </div>
        )}

        <button
          onClick={onReset}
          className="flex items-center gap-1 px-2 sm:px-3 py-[7px] rounded-lg border border-slate-200 text-slate-500 text-xs font-medium hover:bg-slate-50 hover:border-slate-300 transition"
        >
          <RotateCcw size={12} strokeWidth={2} />
          <span className="hidden sm:inline">New chat</span>
        </button>
      </div>
    </div>
  );
}