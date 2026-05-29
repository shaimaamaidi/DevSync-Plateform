import { useState, useRef, useEffect, useCallback } from "react";
import { Send, RotateCcw, GitCommitHorizontal } from "lucide-react";
import type { ClickUpSpaceLightDTO } from "@/api/api";
import { CommitTaskMappingStatus } from "@/api/api";
import { withErrorHandling, defaultOnError } from "@/services/api-error";
import { useNavigate } from "react-router-dom";
import { InsightsChatMessage } from "./insights-chat-message";
import { projectTracingService } from "@/services/project-tracking-service";
import { SpaceSelect } from "./space-select";
import type { InsightsChatMessageType } from "@/types/insights-chat";
import { useClickUpSpacesLight } from "@/hooks/clickup-space-hooks/use-clickup-sapce-light";

let _msgId = 300;
const newId = () => ++_msgId;
 
function agentMsg(content: string, attachment?: InsightsChatMessageType["attachment"]): InsightsChatMessageType {
  return { id: newId(), ts: new Date(), role: "agent", content, attachment };
}
function userMsg(content: string): InsightsChatMessageType {
  return { id: newId(), ts: new Date(), role: "user", content };
}
 
type Step = "select_space" | "enter_commit" | "done" | "finished";
 
interface Props { onReset: () => void; }
 
export function CommitTracerChat({ onReset }: Props) {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);
 
  const [messages, setMessages] = useState<InsightsChatMessageType[]>([
    agentMsg(
      "I'll map a Git commit message to its most likely ClickUp task — using semantic matching to find the best correspondence.\n\nStart by selecting a ClickUp space."
    ),
  ]);
  
  const { spaces, loading: spacesLoading} = useClickUpSpacesLight();
  
  const [selectedSpace, setSelectedSpace] = useState<ClickUpSpaceLightDTO | null>(null);
  const [step, setStep] = useState<Step>("select_space");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
 
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "center"});
  }, [messages.length]);
 
  const push = (msg: InsightsChatMessageType) => setMessages(prev => [...prev, msg]);
 
  const handleSpaceSelect = (space: ClickUpSpaceLightDTO) => {
    setSelectedSpace(space);
    push(userMsg(`Space: ${space.name}`));
    if (!space.repo) {
      push({
        ...agentMsg(
          `Space "${space.name}" has no linked GitHub repository. Commit tracing requires a connected repository — please select a space with GitHub linked.`
        ),
        isRejection: true,
      });
      setStep("finished");
      return;
    } else {
      push(agentMsg(`Space "${space.name}" selected.\n\nNow enter the commit message you want to trace.`));
    }
    setStep("enter_commit");
  };
 
  const handleTrace = async (commit: string) => {
    if (!selectedSpace || !commit.trim()) return;
    push(userMsg(commit));
    setInput("");
    push({ ...agentMsg("Searching for matching task…"), _streaming: true });
    setLoading(true);
 
    const result = await withErrorHandling(
      () => projectTracingService.findTaskByCommit({ commit, space_id: selectedSpace.space_code }),
      "Find task by commit",
      onError(),
    );
    setLoading(false);
    setMessages(prev => prev.filter(m => !m._streaming));
 
    if (!result) return;
 
    if (result.status === CommitTaskMappingStatus.ClickUpEmpty) {
      push({ ...agentMsg(result.message), isRejection: true });
      setStep("finished");
      return;
    }
 
    if (result.status === CommitTaskMappingStatus.NotFound) {
      push(agentMsg(result.message));
      push(agentMsg("You can try with a different commit message."));
      setStep("enter_commit");
      return;
    }
 
    if (result.status === CommitTaskMappingStatus.Found) {
      push(agentMsg(result.message, {
        type: "commit_trace_result",
        data: result,
      }));
      setStep("done");
    }
  };
 
  const canSend = input.trim() && !loading && step === "enter_commit";
 
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-white shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-slate-900 flex items-center justify-center">
            <GitCommitHorizontal size={14} strokeWidth={2} className="text-white" />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-900">Commit Tracer Agent</p>
            <div className="flex items-center gap-1">
              <span className="w-[5px] h-[5px] rounded-full bg-green-500 animate-pulse" />
              <p className="text-[10px] text-slate-400">Git commit → ClickUp task</p>
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
 
        {step === "select_space" && (
          <SpaceSelect
            spaces={spaces}
            spacesLoading={spacesLoading}
            disabled={loading}
            showRepoBadge
            onSelect={handleSpaceSelect}
          />
        )}
 
        <div ref={bottomRef} />
      </div>
 
      {step === "enter_commit" ? (
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
                onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); if (canSend) handleTrace(input); } }}
                placeholder="e.g. fix user session timeout…"
                disabled={loading}
                rows={1}
                className="w-full resize-none bg-transparent text-[13px] text-slate-800 leading-6 outline-none max-h-[120px] overflow-y-auto placeholder:text-slate-400 disabled:opacity-50"
              />
            </div>
            <button
              onClick={() => handleTrace(input)}
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
              ? "Trace complete. Start a new one above."
              : "Waiting for your input…"}
          </p>
        </div>
      ) : null}
    </div>
  );
}
 