import type { ChatMessage as ChatMessageType, UiSprint } from "@/types/backlog";
import { BotMessageSquare, CircleUser, ShieldCheck } from "lucide-react";
import { TypingIndicator } from "./typing-indicator";
import { MessageBubble } from "./message-bubble";
import { MarketCard } from "./market-card";
import { BacklogCard } from "./backlog-card";
import { SprintCard } from "./sprint-card";

interface ChatMessageProps {
  message: ChatMessageType;
  streamingText?: string;
  onMarketSubmit?: (data: any) => void;
  onBacklogSubmit?: (data: any) => void;
}

export function ChatMessage({
  message,
  streamingText = "",
  onMarketSubmit,
  onBacklogSubmit,
}: ChatMessageProps) {
  const isUser = message.role === "user";
  const isRejection = message.isRejection;
  const isStreaming = message._streaming;
  const hasCard =
    message.attachment && !["submitted"].includes(message.attachment?.type);

  return (
    <div
      className={`flex flex-col gap-1 animate-[msg-in_0.22s_ease-out_both] ${
        isUser ? "items-end" : "items-start"
      }`}
    >
      <div
        className={`flex items-start gap-2.5 ${isUser ? "flex-row-reverse" : ""} ${
          hasCard ? "max-w-full w-full" : "max-w-[76%]"
        }`}
      >
        <div
          className={`w-8 h-8 rounded-[9px] flex-shrink-0 flex items-center justify-center bg-slate-900`}
        >
          {isUser ? (
            <CircleUser size={14} strokeWidth={2} className="text-white" />
          ) : (
            <BotMessageSquare size={14} strokeWidth={2} className="text-white" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          {isStreaming ? (
            <div className="px-3.5 py-2.5 text-[13px] leading-[1.7] rounded-xl bg-slate-50 text-slate-800 border border-slate-100 rounded-tl-[3px]">
              {streamingText || <TypingIndicator />}
            </div>
          ) : (
            <MessageBubble
              isUser={isUser}
              isRejection={isRejection}
              content={message.content}
            />
          )}
          {!isStreaming && message.attachment && (
            <AttachmentRenderer
              attachment={message.attachment}
              onMarketSubmit={onMarketSubmit}
              onBacklogSubmit={onBacklogSubmit}
            />
          )}
        </div>
      </div>

      <p
        className={`text-[10px] text-slate-200 m-0 ${
          isUser ? "pr-[42px]" : "pl-[42px]"
        }`}
      >
        {isUser ? "You" : "Agent"} ·{" "}
        {message.ts?.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })}
      </p>
    </div>
  );
}

function AttachmentRenderer({ attachment, onMarketSubmit, onBacklogSubmit }: any) {
  if (!attachment) return null;

  if (attachment.type === "market") {
    return (
      <MarketCard
        data={attachment.data}
        editable={attachment.editable}
        onSubmit={onMarketSubmit}
      />
    );
  }

  if (attachment.type === "submitted") {
    return (
      <div className="flex items-center gap-2 mt-2 px-3 py-2 bg-green-500/[0.08] rounded-[9px] border border-green-500/25 text-[12px] text-green-700 font-medium">
        <ShieldCheck size={14} strokeWidth={2} className="text-green-600 flex-shrink-0" />
        <span>
          {attachment.mode === "backlog_generation"
            ? "Submitted for backlog generation"
            : "Submitted for validation"}
        </span>
      </div>
    );
  }

  if (attachment.type === "backlog") {
    return (
      <BacklogCard
        data={attachment.data}
        editable={attachment.editable}
        onSubmit={onBacklogSubmit}
      />
    );
  }

  if (attachment.type === "sprint") {
    return <SprintCard data={attachment.data as UiSprint[]} />;
  }

  return null;
}