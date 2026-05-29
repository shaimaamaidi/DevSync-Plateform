import { useState, useRef, useEffect, useCallback } from "react";
import { RotateCcw, BarChart2 } from "lucide-react";
import type { ClickUpSpaceLightDTO } from "@/api/api";
import { withErrorHandling, defaultOnError } from "@/services/api-error";
import { useNavigate } from "react-router-dom";
import { InsightsChatMessage } from "./insights-chat-message";
import { projectTracingService } from "@/services/project-tracking-service";
import { SpaceSelect } from "./space-select";
import type { InsightsChatMessageType } from "@/types/insights-chat";
import { useClickUpSpacesLight } from "@/hooks/clickup-space-hooks/use-clickup-sapce-light";

let _msgId = 100;
const newId = () => ++_msgId;
 
function agentMsg(content: string, attachment?: InsightsChatMessageType["attachment"]): InsightsChatMessageType {
  return { id: newId(), ts: new Date(), role: "agent", content, attachment };
}
function userMsg(content: string): InsightsChatMessageType {
  return { id: newId(), ts: new Date(), role: "user", content };
}
 
interface Props { onReset: () => void; }
 
export function ProjectStatusChat({ onReset }: Props) {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);
 
  const [messages, setMessages] = useState<InsightsChatMessageType[]>([
    agentMsg(
      "I'll give you a complete overview of your project — task distribution, last GitHub activity, stale tasks, and unverified completions.\n\nSelect a ClickUp space to get started."
    ),
  ]);

  const { spaces, loading: spacesLoading} = useClickUpSpacesLight();
  
  const [step, setStep] = useState<"select_space" | "done">("select_space");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
 
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [messages.length]);
 
  const push = (msg: InsightsChatMessageType) => setMessages(prev => [...prev, msg]);
 
  const handleSpaceSelect = async (space: ClickUpSpaceLightDTO) => {
    push(userMsg(`Space: ${space.name}`));
    push({ ...agentMsg("Fetching project status…"), _streaming: true });
    setLoading(true);
 
    const result = await withErrorHandling(
      () => projectTracingService.getProjectStatus({
        space_id: space.space_code,
        repo_url: space.repo?.url ?? null,
      }),
      "Get project status",
      onError(),
    );
    setLoading(false);
    setMessages(prev => prev.filter(m => !m._streaming));
 
    if (!result){
      push({ ...agentMsg("Something went wrong. Please try again."), isRejection: true });
      setStep("done");
      return
    };
 
    push(agentMsg("Here is the current status of your project", {
      type: "project_status_result",
      data: result,
    }));
    setStep("done");
  };
 
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-white shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-slate-900 flex items-center justify-center">
            <BarChart2 size={14} strokeWidth={2} className="text-white" />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-900">Project Status Agent</p>
            <div className="flex items-center gap-1">
              <span className="w-[5px] h-[5px] rounded-full bg-green-500 animate-pulse" />
              <p className="text-[10px] text-slate-400">ClickUp · GitHub activity</p>
            </div>
          </div>
        </div>
        <button
          onClick={onReset}
          className="flex items-center gap-1 px-2 py-1.5 rounded-lg border border-slate-200 text-slate-500 text-xs font-medium hover:bg-slate-50 transition"
        >
          <RotateCcw size={11} strokeWidth={2} />
          <span>New</span>
        </button>
      </div>
 
      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-4 [scrollbar-width:thin] [scrollbar-color:#e2e8f0_transparent]">
        {messages.map(msg => (
          <InsightsChatMessage key={msg.id} message={msg} />
        ))}
 
        {step === "select_space" && !loading && (
          <SpaceSelect
            spaces={spaces}
            spacesLoading={spacesLoading}
            disabled={loading}
            onSelect={handleSpaceSelect}
          />
        )}
 
        <div ref={bottomRef} />
      </div>
 
      {step === "done" && (
        <div className="border-t border-slate-100 px-4 py-3 bg-white text-center shrink-0">
          <p className="text-[11px] text-slate-400">Analysis complete. Start a new check above.</p>
        </div>
      )}
    </div>
  );
}
 