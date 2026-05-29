import { useState, useRef, useEffect, useCallback } from "react";
import { CheckCircle, RotateCcw, Send } from "lucide-react";
import type { ClickUpSpaceLightDTO, ClickUpTask, TaskSearchStatus } from "@/api/api";
import { withErrorHandling, defaultOnError } from "@/services/api-error";
import { useNavigate } from "react-router-dom";
import { clickUpService } from "@/services/clickup-service";
import { projectTracingService } from "@/services/project-tracking-service";
import { InsightsChatMessage } from "./insights-chat-message";
import { SpaceSelect } from "./space-select";
import type { InsightsChatMessageType } from "@/types/insights-chat";


let _msgId = 0;
const newId = () => ++_msgId;
 
function agentMsg(content: string, attachment?: InsightsChatMessageType["attachment"]): InsightsChatMessageType {
  return { id: newId(), ts: new Date(), role: "agent", content, attachment };
}
function userMsg(content: string): InsightsChatMessageType {
  return { id: newId(), ts: new Date(), role: "user", content };
}
 
type Step = "select_space" | "enter_description" | "awaiting_confirm" | "done" | "finished";
 
interface Props { onReset: () => void; }
 
export function TaskStatusChat({ onReset }: Props) {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);
 
  const [messages, setMessages] = useState<InsightsChatMessageType[]>([
    agentMsg(
      "I'll help you check whether a ClickUp task is truly completed — by cross-referencing its status with linked GitHub commits and deployments.\n\nPlease start by selecting a ClickUp space below."
    ),
  ]);
  const [spaces, setSpaces] = useState<ClickUpSpaceLightDTO[]>([]);
  const [spacesLoading, setSpacesLoading] = useState(true);
  const [selectedSpace, setSelectedSpace] = useState<ClickUpSpaceLightDTO | null>(null);
  const [step, setStep] = useState<Step>("select_space");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
 
  useEffect(() => {
    clickUpService.getAllSpacesLight()
      .then(setSpaces)
      .catch(() => {})
      .finally(() => setSpacesLoading(false));
  }, []);
 
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [messages.length]);
 
  const push = (msg: InsightsChatMessageType) => setMessages(prev => [...prev, msg]);
 
  const handleSpaceSelect = (space: ClickUpSpaceLightDTO) => {
    setSelectedSpace(space);
    push(userMsg(`Space: ${space.name}`));
    push(agentMsg(`Great! Space "${space.name}" selected.\n\nNow describe the task you want to check — you can use its name or any description you remember.`));
    setStep("enter_description");
  };
 
  const handleSearch = async (description: string) => {
    if (!selectedSpace || !description.trim()) return;
    push(userMsg(description));
    setInput("");
    push({ ...agentMsg("Searching…"), _streaming: true });
    setLoading(true);
 
    const result = await withErrorHandling(
      () => projectTracingService.searchTask({ space_id: selectedSpace.space_code, description: description }),
      "Search task",
      onError(),
    );
    setLoading(false);
 
    if (!result) return;
 
    const status = result.status as TaskSearchStatus;
 
    if (status === "No_TASK_IN_SPACE") {
      push({ ...agentMsg("This space has no tasks yet. There's nothing to check."), isRejection: true });
      setStep("finished");
      return;
    }
 
    if (status === "NO_MATCH") {
      push(agentMsg(result.message));
      setStep("enter_description");
      return;
    }
 
    if (status === "SINGLE_MATCH") {
      push(agentMsg(result.message, {
        type: "task_confirm_single",
        data: { task: result.task?.[0] },
      }));
      setStep("awaiting_confirm");
      return;
    }
 
    if (status === "MULTIPLES_MATCHES") {
      push(agentMsg(result.message, {
        type: "task_select_multiple",
        data: { tasks: result.task },
      }));
      setStep("awaiting_confirm");
      return;
    }
  };
 
  const handleAttachmentAction = async (action: string, payload?: any) => {
    if (action === "confirm_no") {
      push(userMsg("No, that's not the task I'm looking for."));
      push(agentMsg("No problem. Please rephrase your desc and I'll search again."));
      setStep("enter_description");
      return;
    }
 
    if (action === "confirm_yes" || action === "select_task") {
      const task: ClickUpTask = payload;
      if (action === "confirm_yes") {
        push(userMsg("Yes, I confirm this is the task."));
      } else {
        push(userMsg(`I'm referring to the task: ${task.name}`));
      }
      push({ ...agentMsg("Analyzing…"), _streaming: true });
      setLoading(true);
 
      const result = await withErrorHandling(
        () => projectTracingService.synthesizeTaskStatus({
          task,
          repo_url: selectedSpace?.repo?.url ?? null,
        }),
        "Synthesize task status",
        onError(),
      );
      setLoading(false);
      setMessages(prev => prev.filter(m => !m._streaming));
 
      if (!result) return;
 
      push(agentMsg("Here is the analysis result:", {
        type: "task_synthesis_result",
        data: result,
      }));
      setStep("done");
    }
  };
 
  const canSend = input.trim() && !loading && step === "enter_description";
 
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-white shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-slate-900 flex items-center justify-center">
            <CheckCircle size={14} strokeWidth={2} className="text-white" />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-900">Task Status Agent</p>
            <div className="flex items-center gap-1">
              <span className="w-[5px] h-[5px] rounded-full bg-green-500 animate-pulse" />
              <p className="text-[10px] text-slate-400">ClickUp · GitHub cross-check</p>
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
          <InsightsChatMessage
            key={msg.id}
            message={msg}
            onAttachmentAction={handleAttachmentAction}
          />
        ))}
 
        {step === "select_space" && (
          <SpaceSelect
            spaces={spaces}
            spacesLoading={spacesLoading}
            disabled={loading}
            onSelect={handleSpaceSelect}
          />
        )}
 
        <div ref={bottomRef} />
      </div>
 
      {step === "enter_description" ? (
        <div className="border-t border-slate-100 px-3 pt-3 pb-4 bg-white shrink-0">
          <div className="flex items-end gap-2">
            <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus-within:border-slate-400 transition">
              <textarea
                value={input}
                onChange={e => {
                  setInput(e.target.value);
                  e.target.style.height = "auto";
                  e.target.style.height = `${e.target.scrollHeight}px`;
                }}
                onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); if (canSend) handleSearch(input); } }}
                placeholder="Describe the task you want to check…"
                disabled={loading}
                rows={1}
                className="w-full resize-none bg-transparent text-[13px] text-slate-800 leading-6 outline-none max-h-[120px] overflow-y-auto placeholder:text-slate-400 disabled:opacity-50"
              />
            </div>
            <button
              onClick={() => handleSearch(input)}
              disabled={!canSend}
              className={`w-10 h-10 rounded-xl flex items-center justify-center transition shrink-0 ${canSend ? "bg-slate-900 hover:scale-105 active:scale-95" : "bg-slate-200 opacity-30 cursor-default"}`}
            >
              <Send size={13} strokeWidth={2} className={canSend ? "text-white" : "text-slate-400"} />
            </button>
          </div>
          <p className="mt-1 text-[10px] text-slate-300">Press Enter to send · Shift+Enter for new line</p>
        </div>
      ) : step !== "select_space" ? (
        <div className="border-t border-slate-100 px-4 py-3 bg-white text-center shrink-0">
          <p className="text-[11px] text-slate-400">
            {step === "finished"
              ? "Conversation ended."
              : step === "done"
              ? "Analysis complete. Start a new check above."
              : "Waiting for your selection above…"}
          </p>
        </div>
      ) : null}
    </div>
  );
}