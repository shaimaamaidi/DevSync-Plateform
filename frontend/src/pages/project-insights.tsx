import { useState } from "react";
import { CheckCircle, BarChart2, CalendarDays, GitCommitHorizontal, Sparkles } from "lucide-react";
import { TaskStatusChat } from "@/components/ui/task-status-chat";
import { CommitTracerChat } from "@/components/ui/commit-tracer-chat";
import { WeeklySummaryChat } from "@/components/ui/weekly-summary-chat";
import { ProjectStatusChat} from "@/components/ui/project-status-chat";


type UseCase = "task_status" | "project_status" | "weekly_summary" | "commit_tracer";

const USE_CASES: {
  id: UseCase;
  icon: React.ElementType;
  label: string;
  description: string;
}[] = [
  {
    id: "task_status",
    icon: CheckCircle,
    label: "Task Status",
    description: "Is this task truly completed?",
  },
  {
    id: "project_status",
    icon: BarChart2,
    label: "Project Status",
    description: "Overall project health & activity",
  },
  {
    id: "weekly_summary",
    icon: CalendarDays,
    label: "Weekly Summary",
    description: "What was done this week?",
  },
  {
    id: "commit_tracer",
    icon: GitCommitHorizontal,
    label: "Commit Tracer",
    description: "Which task does this commit belong to?",
  },
];

function ChatZone({ selected, resetKey, onReset }: { selected: UseCase; resetKey: number; onReset: () => void }) {
  const props = { onReset, key: resetKey };
  switch (selected) {
    case "task_status":    return <TaskStatusChat {...props} />;
    case "project_status": return <ProjectStatusChat {...props} />;
    case "weekly_summary": return <WeeklySummaryChat {...props} />;
    case "commit_tracer":  return <CommitTracerChat {...props} />;
  }
}

export function ProjectInsights() {
  const [selected, setSelected] = useState<UseCase | null>(null);
  const [resetKey, setResetKey] = useState(0);
  
  const handleSelect = (id: UseCase) => {
    if (selected === id) return;
    setSelected(id);
    setResetKey(k => k + 1);
  };

  const handleReset = () => {
    setResetKey(k => k + 1);
  };

  return (
    <div className="w-full space-y-6 py-2">

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {USE_CASES.map(({ id, icon: Icon, label, description }) => {
          const isActive = selected === id;
          return (
            <button
              key={id}
              onClick={() => handleSelect(id)}
              className={[
                "relative flex flex-col items-start gap-2 rounded-xl border px-4 py-3 text-left transition-all duration-200",
                isActive
                  ? "border-[#0E9E82] bg-[#0E9E82] shadow-md"
                  : "border-slate-200 bg-white hover:border-slate-400 hover:bg-slate-50",
              ].join(" ")}
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${isActive ? "bg-white/10" : "bg-slate-100"}`}>
                <Icon size={16} strokeWidth={2} className={isActive ? "text-white" : "text-slate-600"} />
              </div>
              <div>
                <p className={`text-[13px] font-semibold leading-tight ${isActive ? "text-white" : "text-slate-800"}`}>{label}</p>
                <p className={`text-[11px] mt-0.5 leading-snug ${isActive ? "text-slate-300" : "text-slate-400"}`}>{description}</p>
              </div>
              {isActive && (
                <span className="absolute top-2 right-2 w-[6px] h-[6px] rounded-full bg-white animate-pulse" />
              )}
            </button>
          );
        })}
      </div>

      <div
        className={[
          "overflow-hidden rounded-2xl border border-slate-200 shadow-[0_4px_24px_rgba(0,0,0,0.06),0_1px_3px_rgba(0,0,0,0.04)] bg-white transition-all duration-300 ease-out",
          selected
            ? "opacity-100 translate-y-0 max-h-[800px] h-[calc(100vh-18rem)] min-h-[500px]"
            : "opacity-0 translate-y-2 max-h-0 min-h-0 pointer-events-none",
        ].join(" ")}
      >
        {selected ? (
          <ChatZone selected={selected} resetKey={resetKey} onReset={handleReset} />
        ) : null}
      </div>

      {!selected && (
        <div className="flex flex-col items-center justify-center gap-3 py-16 text-center animate-[msg-in_0.22s_ease-out_both]">
          <div className="w-14 h-14 rounded-2xl bg-[#0E9E82]flex items-center justify-center shadow-[0_8px_24px_rgba(15,23,42,0.15)]">
            <Sparkles size={24} strokeWidth={1.5} className="text-white" />
          </div>
          <div>
            <p className="text-[16px] font-bold text-slate-900 tracking-tight mb-1">Project Insights</p>
            <p className="text-[13px] text-slate-400 max-w-sm leading-relaxed">
              Select one of the four options above to start an analysis — task status, project health, weekly activity, or commit traceability.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}