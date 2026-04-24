import { useChatLogic } from "@/hooks/use-chat-logic";
import { useEffect, useRef } from "react";
import { ChatHeader } from "./ui/chat-header";
import { EmptyState } from "./ui/empty-state";
import { ChatMessage } from "./ui/chat-message";
import { ChatInput } from "./ui/chat-input";

export function BacklogGenerationChat() {
  const {
    messages,
    input,
    setInput,
    loading,
    step,
    streamingText,
    resetChat,
    handleSend,
    handleMarketSubmit,
    handleBacklogSubmit,
  } = useChatLogic();

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, streamingText]);

  return (
    <div className="flex flex-col h-screen max-h-[860px] bg-white rounded-2xl border border-slate-200 overflow-hidden font-[-apple-system,BlinkMacSystemFont,'Inter','Segoe_UI',sans-serif] shadow-[0_4px_24px_rgba(0,0,0,0.06),0_1px_3px_rgba(0,0,0,0.04)]">
      <ChatHeader step={step} onReset={resetChat} />

      <div className="flex-1 overflow-y-auto px-5 py-6 flex flex-col gap-5 [scrollbar-width:thin] [scrollbar-color:#e2e8f0_transparent]">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              streamingText={streamingText}
              onMarketSubmit={handleMarketSubmit}
              onBacklogSubmit={handleBacklogSubmit}
            />
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {step === "idle" ? (
        <ChatInput
          value={input}
          onChange={setInput}
          onSend={() => handleSend(input)}
          disabled={loading}
          placeholder="Describe the product you want to build…"
        />
      ) : (
        <div className="border-t border-slate-100 px-4 py-4 bg-white text-center">
          <p className="text-[12px] text-slate-400">
            Use the cards above to interact with the agent…
          </p>
        </div>
      )}
    </div>
  );
}