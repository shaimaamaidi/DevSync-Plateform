import { useCallback, useRef, useState } from "react";
import type { ChatMessage, MarketSummary, UiEpic, BacklogPayload } from "@/types/backlog";
import { readSseStream } from "@/utils/stream-parser";
import { extractBacklogPayload, isClarificationNeeded, isConflictsDetected, isRefinedMarketIntelligence, isSprintPlanning } from "@/lib/guards";
import {
  areBacklogsEqual,
  areMarketSummariesEqual,
  backlogToUi,
  cloneMarketSummary,
  normalizeMarketSummary,
  refinedToSummary,
  sprintPlanningToUi,
  uiToBacklog,
} from "@/lib/backlog.mapper";
import { backlogGenerationService } from "@/services/backlog-generation-service";
import { emitAxiosError, onAxiosError, type AxiosErrorEvent } from "@/api/axios-interceptor";
import type { ErrorAction } from "@/types/api-error-type";

type Step = "idle" | "clarifying" | "market_review" | "backlog_edit" | "finalizing" | "done";

type StreamFailed = { readonly __streamFailed: true; action: ErrorAction };

function streamFailed(action: ErrorAction): StreamFailed {
  return { __streamFailed: true, action };
}

function isStreamFailed(v: unknown): v is StreamFailed {
  return typeof v === "object" && v !== null && (v as any).__streamFailed === true;
}

function shouldOfferRetry(action: ErrorAction): boolean {
  return (
    action === "RETRY_THEN_SERVICE_ERROR" ||
    action === "RETRY_THEN_DATA_ERROR" ||
    action === "NOTIFY"
  );
}

function emitUnexpectedError(message = "An unexpected error occurred.") {
  emitAxiosError({ action: "NOTIFY", message, code: null });
}

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
  const [currentToolName, setCurrentToolName] = useState<string | null>(null);
  const [clarifyingMode, setClarifyingMode] = useState<"clarification" | "conflicts">("clarification");

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
    setClarifyingMode("clarification");
    streamingMsgIdRef.current = null;
    threadIdRef.current = null;
    lastRefinedMarketRef.current = null;
    lastBacklogPayloadRef.current = null;
    lastSubmittedMarketRef.current = null;
  };

  const runStream = async (
    streamPromise: Promise<ReadableStream<Uint8Array>>,
    lastEmittedAction: { current: ErrorAction | null },
  ) => {
    try {
      const stream = await streamPromise;
      setStreamingText("");
      setCurrentToolName(null);
      const result = await readSseStream(
        stream,
        (chunk) => { setStreamingText((prev) => prev + chunk); },
        (name) => { setCurrentToolName(name); }, 
      );
      setStreamingText("");
      setCurrentToolName(null);
      return result;
    } catch {
      setStreamingText("");
      setCurrentToolName(null);
      return streamFailed(lastEmittedAction.current ?? "NOTIFY");
    }
  };


  const handleSend = async (text: string, isRetry = false) => {
    if (!text.trim() || loading) return;
    if (!isRetry && step !== "idle") return;

    if (!isRetry) {
      setInput("");
      addMsg({ role: "user", content: text });
    }

    setLoading(true);
    const agentMsgId = addMsg({ role: "agent", content: "", _streaming: true });
    streamingMsgIdRef.current = agentMsgId;

    const lastEmittedAction: { current: ErrorAction | null } = { current: null };
    const unsub = onAxiosErrorOnce((e) => { lastEmittedAction.current = e.action; });

    try {
      const result = await runStream(
        backlogGenerationService.start({ description: text }),
        lastEmittedAction,
      );

      if (isStreamFailed(result)) {
        const isNetworkDown = result.action === "NETWORK_DOWN";
        if (isNetworkDown) {
          updateMsg(agentMsgId, {
            _streaming: false,
            content: "Connection lost. Please check your internet connection and try again.",
          });
          setStep("done");
          return;
        }

        const isSessionError = result.action === "RETRY_THEN_LOGOUT";
        updateMsg(agentMsgId, {
          _streaming: false,
          content: isSessionError
            ? "Your session could not be restored. You will be redirected to login."
            : "The request didn't go through. You can try again.",
          ...(shouldOfferRetry(result.action) && { onRetry: () => handleSend(text, true) }),
        });
        return;
      }

      const { threadId, text: agentText, json, invalidDescription  } = result;
      if (isClarificationNeeded(json)) {
        threadIdRef.current = threadId;
        setStep("clarifying");
        setClarifyingMode("clarification");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: agentText || json.question,
          attachment: {
            type: "clarification",
            data: { question: json.question, missing_dimension: json.missing_dimension },
          },
        });
        return;
      }
      if (isConflictsDetected(json)) {
        threadIdRef.current = threadId;
        setStep("clarifying");
        setClarifyingMode("conflicts");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: json.question,
          attachment: {
            type: "conflicts",
            data: { conflicts: json.conflicts, question: json.question },
          },
        });
        return;
      }
      if (invalidDescription) {
        updateMsg(agentMsgId, {
          _streaming: false,
          content: invalidDescription.message,
        });
        setStep("done");
        return;
      }

      if (!threadId || !isRefinedMarketIntelligence(json)) {
        emitUnexpectedError("The agent returned an unexpected response.");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: "The agent returned an unexpected response.",
        });
        return;
      }

      threadIdRef.current = threadId;
      lastRefinedMarketRef.current = json;

      setStep("market_review");
      updateMsg(agentMsgId, {
        _streaming: false,
        content: agentText || "Market intelligence generated. Please review and submit.",
        attachment: { type: "market", data: refinedToSummary(json), editable: true },
      });
    } catch {
      emitUnexpectedError();
      updateMsg(agentMsgId, { _streaming: false, content: "An unexpected error occurred." });
    } finally {
      unsub();
      setLoading(false);
    }
  };


  const handleMarketSubmit = async (editedSummary: MarketSummary, isRetry = false) => {
    const submittedSummary = cloneMarketSummary(normalizeMarketSummary(editedSummary));

    if (!isRetry) {
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
    const lastEmittedAction: { current: ErrorAction | null } = { current: null };
    const unsub = onAxiosErrorOnce((e) => { lastEmittedAction.current = e.action; });

    try {
      if (!threadIdRef.current || !lastRefinedMarketRef.current) {
        emitUnexpectedError("Missing session context. Please restart.");
        updateMsg(agentMsgId, { _streaming: false, content: "Missing session context. Please restart." });
        return;
      }

      const result = await runStream(
        backlogGenerationService.reply({
          thread_id: threadIdRef.current,
          tool_result: JSON.stringify({ ...lastRefinedMarketRef.current, is_valid: false }),
          user_result: JSON.stringify(
            cloneMarketSummary(normalizeMarketSummary(lastSubmittedMarketRef.current ?? submittedSummary))
          ),
        }),
        lastEmittedAction,
      );

      if (isStreamFailed(result)) {
        const isNetworkDown = result.action === "NETWORK_DOWN";
        if (isNetworkDown) {
          updateMsg(agentMsgId, {
            _streaming: false,
            content: "Connection lost. Please check your internet connection and try again.",
          });
          setStep("done");
          return;
        }

        const isSessionError = result.action === "RETRY_THEN_LOGOUT";
        updateMsg(agentMsgId, {
          _streaming: false,
          content: isSessionError
            ? "Your session could not be restored. You will be redirected to login."
            : "The request didn't go through. You can try again.",
          ...(shouldOfferRetry(result.action) && { onRetry: () => handleMarketSubmit(editedSummary, true) }),
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
        emitUnexpectedError("The agent returned an unexpected response.");
        setStep("market_review");
        updateMsg(agentMsgId, { _streaming: false, content: "The agent returned an unexpected response." });
      }
    } catch {
      emitUnexpectedError();
      setStep("market_review");
      updateMsg(agentMsgId, { _streaming: false, content: "An unexpected error occurred." });
    } finally {
      unsub();
      setLoading(false);
    }
  };


  const handleBacklogSubmit = async (editedEpics: UiEpic[], isRetry = false) => {
    const userBacklog = uiToBacklog(editedEpics);
    const hasBacklogChanges = !areBacklogsEqual(userBacklog, lastBacklogPayloadRef.current!);
    const submissionBacklog = hasBacklogChanges
      ? userBacklog
      : (lastBacklogPayloadRef.current ?? userBacklog);

    if (!isRetry) {
      setMessages((prev) =>
        prev.map((m) =>
          m.attachment?.type === "backlog"
            ? { ...m, attachment: { ...m.attachment, type: "backlog", data: editedEpics, editable: false } }
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
    const lastEmittedAction: { current: ErrorAction | null } = { current: null };
    const unsub = onAxiosErrorOnce((e) => { lastEmittedAction.current = e.action; });

    try {
      if (!threadIdRef.current || !lastBacklogPayloadRef.current) {
        emitUnexpectedError("Missing session context. Please restart.");
        setStep("backlog_edit");
        updateMsg(agentMsgId, { _streaming: false, content: "Missing session context. Please restart." });
        return;
      }

      const toolResultPayload = hasBacklogChanges
        ? lastBacklogPayloadRef.current
        : submissionBacklog;

      const result = await runStream(
        backlogGenerationService.replyBacklog({
          thread_id: threadIdRef.current,
          user_result: JSON.stringify(submissionBacklog),
          tool_result: JSON.stringify(toolResultPayload),
        }),
        lastEmittedAction,
      );

      if (isStreamFailed(result)) {
        const isNetworkDown = result.action === "NETWORK_DOWN";
        if (isNetworkDown) {
          updateMsg(agentMsgId, {
            _streaming: false,
            content: "Connection lost. Please check your internet connection and try again.",
          });
          setStep("done");
          return;
        }

        const isSessionError = result.action === "RETRY_THEN_LOGOUT";
        updateMsg(agentMsgId, {
          _streaming: false,
          content: isSessionError
            ? "Your session could not be restored. You will be redirected to login."
            : "The request didn't go through. You can try again.",
          ...(shouldOfferRetry(result.action) && { onRetry: () => handleBacklogSubmit(editedEpics, true) }),
        });
        return;
      }

      const { text: agentText, json } = result;
      const correctedBacklogPayload = extractBacklogPayload(json);
      const sprintData = isSprintPlanning(json) ? sprintPlanningToUi(json) : null;

      if (!hasBacklogChanges) {
        if (correctedBacklogPayload) lastBacklogPayloadRef.current = correctedBacklogPayload;
        setStep("done");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: agentText || "Sprint planning generated.",
          ...(sprintData ? { attachment: { type: "sprint", data: sprintData } } : {}),
        });

        if (sprintData) {
          addMsg({
            role: "agent",
            content: "",
            attachment: { type: "clickup_management", data: sprintData },
          });
        } else {
          onNavigate?.("/backlog", { state: { epics: backlogToUi(lastBacklogPayloadRef.current!) } });
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
        emitUnexpectedError("The agent returned an unexpected response.");
        setStep("done");
        updateMsg(agentMsgId, {
          _streaming: false,
          content: agentText || "Backlog refinement completed.",
          ...(sprintData ? { attachment: { type: "sprint", data: sprintData } } : {}),
        });
      }
    } catch {
      emitUnexpectedError();
      setStep("backlog_edit");
      updateMsg(agentMsgId, { _streaming: false, content: "An unexpected error occurred." });
    } finally {
      unsub();
      setLoading(false);
    }
  };

  const handleClarificationReply = async (clarificationText: string, isRetry = false) => {
    if (!clarificationText.trim() || loading) return;

    if (!isRetry) {
      addMsg({ role: "user", content: clarificationText });
    }

    setStep("idle");
    await handleSend(clarificationText, false);
  };

  const handleClickUpYes = (sprintData: any) => {
    localStorage.setItem('sprint_backlog', JSON.stringify(sprintData));
    onNavigate?.('/backlog-tasks');
  };

  const handleClickUpNo = () => {
    addMsg({
      role: "agent",
      content: "This chat session has ended. If you'd like to create a new backlog, click the button at the top right of the conversation.",
    });
  };

  return {
    messages,
    input,
    setInput,
    loading,
    step,
    clarifyingMode,
    streamingText,
    addMsg,
    updateMsg,
    resetChat,
    handleSend,
    handleMarketSubmit,
    handleBacklogSubmit,
    handleClarificationReply,
    handleClickUpYes,
    handleClickUpNo,
    currentToolName
  };
}

function onAxiosErrorOnce(cb: (e: AxiosErrorEvent) => void): () => void {
  let fired = false;
  const unsub = onAxiosError((e: AxiosErrorEvent) => {
    if (!fired) {
      fired = true;
      cb(e);
    }
  });
  return unsub;
}