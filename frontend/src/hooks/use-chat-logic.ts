import { useCallback, useRef, useState } from "react";
import type { ChatMessage, MarketSummary, UiEpic, BacklogPayload } from "@/types/backlog";
import { readSseStream } from "@/utils/stream-parser";
import { extractBacklogPayload, isRefinedMarketIntelligence, isSprintPlanning } from "@/utils/type-guards";
import {
  areBacklogsEqual,
  areMarketSummariesEqual,
  backlogToUi,
  cloneMarketSummary,
  normalizeMarketSummary,
  refinedToSummary,
  sprintPlanningToUi,
  uiToBacklog,
} from "@/utils/backlog.mapper";
import { backlogGenerationService } from "@/services/backlog-generation-service";
import { showErrorToast } from "@/components/global-toaster";
import { authService } from "@/services/auth-service";
import { SseError } from "@/types/sse-error";

type Step = "idle" | "market_review" | "backlog_edit" | "finalizing" | "done";

export function useChatLogic(onNavigate?: (path: string, opts?: any) => void) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<Step>("idle");
  const [streamingText, setStreamingText] = useState("");

  const threadIdRef = useRef<string | null>(null);
  const lastRefinedMarketRef = useRef<any>(null);
  const lastBacklogPayloadRef = useRef<BacklogPayload | null>(null);
  const lastSubmittedMarketRef = useRef<MarketSummary | null>(null);
  const streamingMsgIdRef = useRef<number | null>(null);

  const addMsg = useCallback((msg: Omit<ChatMessage, "id" | "ts">) => {
    const id = Date.now() + Math.random();
    setMessages((prev) => [...prev, { id, ts: new Date(), ...msg }]);
    return id;
  }, []);

  const updateMsg = useCallback((id: number, patch: Partial<ChatMessage>) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? { ...m, ...patch } : m))
    );
  }, []);

  const resetChat = () => {
    setMessages([]);
    setInput("");
    setLoading(false);
    setStep("idle");
    setStreamingText("");
    streamingMsgIdRef.current = null;
    threadIdRef.current = null;
    lastRefinedMarketRef.current = null;
    lastBacklogPayloadRef.current = null;
    lastSubmittedMarketRef.current = null;
  };

  const runStream = async (
  streamPromise: Promise<ReadableStream<Uint8Array>>,
  ) => {
    try {
      const stream = await streamPromise;
      setStreamingText("");
      const result = await readSseStream(stream, (chunk) => {
        setStreamingText((prev) => prev + chunk);
      });
      setStreamingText("");
      return result;
    } catch (error) {
      if (error instanceof SseError) {
        if (error.errorType === 'backend_error') {
          showErrorToast(error.message, 'Operation failed');
          return { isBackendError: true } as const;
        } else {
          await authService.logout();
          onNavigate?.('/login');
          showErrorToast('A server error occurred. Please try again later.');
        }
      } else {
        showErrorToast('A server error occurred. Please try again later.');
      }
      return null;
    }
  };

  const handleSend = async (text: string, isRetry = false) => {
    if (!text.trim() || loading) 
      return;

    if (!isRetry && step !== "idle") 
      return;

    if (!isRetry){
      setInput("");
      addMsg({ role: "user", content: text });
    }
    
    setLoading(true);

    const agentMsgId = addMsg({ role: "agent", content: "", _streaming: true });
    streamingMsgIdRef.current = agentMsgId;

    try {
      const result = await runStream(
        backlogGenerationService.start({ description: text })
      );

      if (!result) {
        updateMsg(agentMsgId, {
          _streaming: false,
          content: "The request didn't go through. You can try again.",
        });
        return;
      }

      if ('isBackendError' in result) {
        updateMsg(agentMsgId, {
          _streaming: false,
          content: "The agent encountered an issue processing your request.",
          onRetry: () => handleSend(text, true), 
        });
        return;
      }

      const { threadId, text: agentText, json } = result;
      if (!threadId) throw new Error("Missing thread_id");
      if (!isRefinedMarketIntelligence(json)) throw new Error("Unexpected response");

      threadIdRef.current = threadId;
      lastRefinedMarketRef.current = json;
      const summary = refinedToSummary(json);

      setStep("market_review");
      updateMsg(agentMsgId, {
        _streaming: false,
        content: agentText || "Market intelligence generated. Please review and submit.",
        attachment: { type: "market", data: summary, editable: true },
      });
    } catch {
      updateMsg(agentMsgId, {
        _streaming: false,
        content: "The agent returned an unexpected response.",
        onRetry: () => handleSend(text, true), 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleMarketSubmit = async (editedSummary: MarketSummary, isRetry = false) => {
    const submittedSummary = cloneMarketSummary(normalizeMarketSummary(editedSummary));
    
    if(!isRetry){
      const baselineSummary = lastRefinedMarketRef.current
        ? cloneMarketSummary(refinedToSummary(lastRefinedMarketRef.current))
        : submittedSummary;
      const hasMarketChanges = !areMarketSummariesEqual(submittedSummary, baselineSummary);

      setMessages((prev) =>
        prev.map((m) =>
          m.attachment?.type === "market"
            ? { ...m, attachment: { ...m.attachment, editable: false, data: submittedSummary } }
            : m
        )
      );
      lastSubmittedMarketRef.current = submittedSummary;

      addMsg({
        role: "user",
        content: hasMarketChanges
          ? "Market intelligence reviewed and submitted."
          : "Market intelligence submitted for backlog generation.",
        attachment: {
          type: "submitted",
          mode: hasMarketChanges ? "validation" : "backlog_generation",
        },
      });
    }
      
    setLoading(true);

    const agentMsgId = addMsg({ role: "agent", content: "", _streaming: true });

    try {
      if (!threadIdRef.current || !lastRefinedMarketRef.current) {
        throw new Error("Missing context");
      }

      const result = await runStream(
        backlogGenerationService.reply({
          thread_id: threadIdRef.current,
          tool_result: JSON.stringify({
            ...lastRefinedMarketRef.current,
            is_valid: false,
          }),
          user_result: JSON.stringify(
            cloneMarketSummary(
              normalizeMarketSummary(
                lastSubmittedMarketRef.current ?? submittedSummary
              )
            )
          ),
        })
      );

      if (!result) {
        setStep("market_review");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: "The request didn't go through. You can try again.",
        });
        return;
      }
      
      if ('isBackendError' in result) {
        setStep("market_review");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: "The agent encountered an issue processing your request.",
          onRetry: () => handleMarketSubmit(editedSummary, true),
        });
        return;
      }

      const { text: agentText, json } = result;
      const backlogPayload = extractBacklogPayload(json);

      if (backlogPayload) {
        lastBacklogPayloadRef.current = backlogPayload;
        setStep("backlog_edit");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: agentText || "Backlog generated. You can now refine it.",
          attachment: { type: "backlog", data: backlogToUi(backlogPayload), editable: true },
        });
      } else if (isRefinedMarketIntelligence(json)) {
        lastRefinedMarketRef.current = json;
        lastSubmittedMarketRef.current = cloneMarketSummary(refinedToSummary(json));
        setStep("market_review");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: agentText || "Please review the refined market intelligence.",
          attachment: { type: "market", data: refinedToSummary(json), editable: true },
          isRejection: json.is_valid === false,
        });
      } else {
        setStep("market_review");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: "The agent returned an unexpected response.",
          onRetry: () => handleMarketSubmit(editedSummary, true),
        });
      }
    } catch {
      setStep("market_review");
      updateMsg(agentMsgId, {
        _streaming: false,
        content: "The agent returned an unexpected response.",
        onRetry: () => handleMarketSubmit(editedSummary, true), 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBacklogSubmit = async (editedEpics: UiEpic[], isRetry = false) => {
    const userBacklog = uiToBacklog(editedEpics);
    const hasBacklogChanges = !areBacklogsEqual(
      userBacklog,
      lastBacklogPayloadRef.current!
    );
    const submissionBacklog = hasBacklogChanges
      ? userBacklog
      : (lastBacklogPayloadRef.current ?? userBacklog);

    if(!isRetry){
      setMessages((prev) =>
        prev.map((m) =>
          m.attachment?.type === "backlog"
            ? { ...m, attachment: { ...m.attachment, type: "backlog", data: editedEpics, editable: false, } }
            : m
        )
      );

      addMsg({
        role: "user",
        content: hasBacklogChanges
          ? "Backlog changes submitted for refinement."
          : "Backlog submitted for finishing.",
        attachment: {
          type: "submitted",
          mode: hasBacklogChanges ? "backlog_refinement" : "backlog_finishing",
        },
      });
    }

    setStep("finalizing");
    setLoading(true);

    const agentMsgId = addMsg({ role: "agent", content: "", _streaming: true });

    try {
      if (!threadIdRef.current || !lastBacklogPayloadRef.current) {
        throw new Error("Missing context");
      }

      const toolResultPayload = hasBacklogChanges
        ? lastBacklogPayloadRef.current
        : submissionBacklog;

      const result = await runStream(
        backlogGenerationService.replyBacklog({
          thread_id: threadIdRef.current,
          user_result: JSON.stringify(submissionBacklog),
          tool_result: JSON.stringify(toolResultPayload),
        })
      );

      if (!result) {
        setStep("backlog_edit");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: "The request didn't go through. You can try again.",
        });
        return;
      }

      if ('isBackendError' in result) {
        setStep("backlog_edit");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: "The agent encountered an issue processing your request.",
          onRetry: () => handleBacklogSubmit(editedEpics, true), 
        });
        return;
      }

      const { text: agentText, json } = result;

      const correctedBacklogPayload = extractBacklogPayload(json);
      const sprintData = isSprintPlanning(json) ? sprintPlanningToUi(json) : null;

      if (!hasBacklogChanges) {
        if (correctedBacklogPayload) {
          lastBacklogPayloadRef.current = correctedBacklogPayload;
        }
        setStep("done");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: agentText || "Sprint planning generated.",
          ...(sprintData ? { attachment: { type: "sprint", data: sprintData } } : {}),
        });

        if (!sprintData) {
          onNavigate?.("/backlog", {
            state: { epics: backlogToUi(lastBacklogPayloadRef.current!) },
          });
        }
      } else if (correctedBacklogPayload) {
        lastBacklogPayloadRef.current = correctedBacklogPayload;
        setStep("backlog_edit");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: agentText || "Backlog refined. Review and continue.",
          attachment: { type: "backlog", data: backlogToUi(correctedBacklogPayload), editable: true },
        });
      } else {
        setStep("done");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: agentText || "Backlog refinement completed.",
          ...(sprintData ? { attachment: { type: "sprint", data: sprintData } } : {}),
        });
      }
    } catch {
      setStep("backlog_edit");
      updateMsg(agentMsgId, {
          _streaming: false,
          content: "The agent returned an unexpected response.",
          onRetry: () => handleBacklogSubmit(editedEpics, true), 
        });
    } finally {
      setLoading(false);
    }
  };

  return {
    messages,
    input,
    setInput,
    loading,
    step,
    streamingText,
    addMsg,
    updateMsg,
    resetChat,
    handleSend,
    handleMarketSubmit,
    handleBacklogSubmit,
  };
}