import type { ChatMessage as ChatMessageType } from "@/types/backlog";
import { BotMessageSquare, CircleUser, RefreshCcw } from "lucide-react";
import { MessageBubble } from "./message-bubble";
import { AttachmentRenderer } from "./attachment-renderer";
import { BacklogTypingIndicator } from "./backlog-typing-indicator";

interface ChatMessageProps {
  message: ChatMessageType;
  streamingText?: string;
  currentToolName?: string | null;
  onMarketSubmit?: (data: any) => void;
  onBacklogSubmit?: (data: any) => void;
  onClickUpYes?: (data: any) => void;
  onClickUpNo?: (data: any) => void;
}

export function BacklogChatMessage({
  message,
  streamingText = "",
  currentToolName,
  onMarketSubmit,
  onBacklogSubmit,
  onClickUpYes,
  onClickUpNo,
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
        className={`flex items-start gap-2 sm:gap-2.5 ${isUser ? "flex-row-reverse" : ""} ${
          hasCard ? "max-w-full w-full" : "max-w-[90%] sm:max-w-[76%]"
        }`}
      >
        <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-[9px] flex-shrink-0 flex items-center justify-center bg-slate-900">
          {isUser ? (
            <CircleUser size={13} strokeWidth={2} className="text-white" />
          ) : (
            <BotMessageSquare size={13} strokeWidth={2} className="text-white" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          {isStreaming ? (
            <div className="px-3 sm:px-3.5 py-2.5 text-[13px] leading-[1.7] rounded-xl bg-slate-50 text-slate-800 border border-slate-100 rounded-tl-[3px]">
              {streamingText || <BacklogTypingIndicator toolName={currentToolName} />}
            </div>
          ) : (
            <MessageBubble
              isUser={isUser}
              isRejection={isRejection}
              content={message.content}
            />
          )}

          {!isStreaming && message.onRetry && (
            <div className="mt-2">
              <button
                onClick={message.onRetry}
                className="flex items-center gap-1.5 px-2.5 py-1.5 text-[12px] font-medium text-slate-500 hover:text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg border border-slate-200 transition-colors cursor-pointer"
              >
                <RefreshCcw size={12} strokeWidth={2} />
                Try again
              </button>
            </div>
          )}

          {!isStreaming && message.attachment && (
            <AttachmentRenderer
              attachment={message.attachment}
              onMarketSubmit={onMarketSubmit}
              onBacklogSubmit={onBacklogSubmit}
              onClickUpYes={onClickUpYes}
              onClickUpNo={onClickUpNo}
            />
          )}
        </div>
      </div>

      <p
        className={`text-[10px] text-slate-200 m-0 ${
          isUser ? "pr-[36px] sm:pr-[42px]" : "pl-[36px] sm:pl-[42px]"
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
