import { useChatLogic } from "@/hooks/use-chat-logic";
import { useEffect, useRef } from "react";
import { ChatHeader } from "@/components/ui/backlog-generation-chat/chat-header";
import { EmptyState } from "@/components/ui/backlog-generation-chat/empty-state";
import { BacklogChatMessage } from "@/components/ui/backlog-generation-chat/backlog-chat-message";
import { ChatInput } from "@/components/ui/backlog-generation-chat/chat-input";
import { useIsMobile } from "@/hooks/use-mobile";

export default function BacklogGenerationChatPage() {
  const {
    messages,
    input,
    setInput,
    loading,
    step,
    clarifyingMode,
    streamingText,
    resetChat,
    handleSend,
    handleMarketSubmit,
    handleBacklogSubmit,
    handleClarificationReply,
    handleClickUpYes,
    handleClickUpNo,
    currentToolName,
  } = useChatLogic();

  const isMobile = useIsMobile();
  const bottomRef = useRef<HTMLDivElement>(null);
  const isStreamingRef = useRef(false);
  const prevMessagesLengthRef = useRef(messages.length);

  useEffect(() => {
    const prev = prevMessagesLengthRef.current;
    prevMessagesLengthRef.current = messages.length;
    if (messages.length > prev) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages.length]);

  useEffect(() => {
    if (messages.length === 0) return;

    if (streamingText && !isStreamingRef.current) {
      isStreamingRef.current = true;
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    } else if (!streamingText && isStreamingRef.current) {
      isStreamingRef.current = false;
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [streamingText, messages.length]);

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div
        className={[
          "flex flex-col overflow-hidden flex-1 min-h-0",
          isMobile
            ? ""
            : "h-[calc(100vh-16rem)] max-h-[800px] min-h-[550px] rounded-2xl border border-slate-200 shadow-[0_4px_24px_rgba(0,0,0,0.06),0_1px_3px_rgba(0,0,0,0.04)]",
        ].join(" ")}
      >
        <ChatHeader step={step} clarifyingMode={clarifyingMode} onReset={resetChat} />

        <div className="flex-1 overflow-y-auto px-3 sm:px-5 py-4 sm:py-6 flex flex-col gap-4 sm:gap-5 [scrollbar-width:thin] [scrollbar-color:#e2e8f0_transparent]">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            messages.map((message) => (
              <BacklogChatMessage
                key={message.id}
                message={message}
                streamingText={streamingText}
                currentToolName={currentToolName} 
                onMarketSubmit={handleMarketSubmit}
                onBacklogSubmit={handleBacklogSubmit}
                onClickUpYes={handleClickUpYes}
                onClickUpNo={handleClickUpNo}
              />
            ))
          )}
          <div ref={bottomRef} />
        </div>

        {step === "idle" || step === "clarifying" ? (
          <ChatInput
            value={input}
            onChange={setInput}
            onSend={() =>
              step === "clarifying"
                ? handleClarificationReply(input)
                : handleSend(input)
            }
            disabled={loading}
            placeholder={
                  step === "clarifying"
                    ? "Answer the agent's question…"
                    : "Describe the product you want to build…"
                }
          />
        ) : (
          <div className="border-t border-slate-100 px-4 py-3 sm:py-4 bg-white text-center">
            <p className="text-[12px] text-slate-400">
              Use the cards above to interact with the agent…
            </p>
          </div>
        )}
      </div>
    </div>
  );
}