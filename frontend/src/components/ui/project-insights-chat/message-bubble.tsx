import { AlertTriangle } from "lucide-react";

export function MessageBubble({ isUser, isRejection, content }: { isUser: boolean; isRejection?: boolean; content: string }) {
  return (  
    <div
      className={[
        "px-3.5 py-2.5 text-[13px] leading-[1.7] rounded-xl",
        "bg-slate-50 text-slate-800 border border-slate-100",
        isUser ? "rounded-tr-[3px]" : "rounded-tl-[3px]",
        isRejection ? "bg-red-500/[0.06] border-red-500/[0.18] text-red-700" : "",
      ].join(" ")}
    > 
      {isRejection && (
        <div className="flex items-center gap-1.5 mb-2 pb-2 border-b border-red-500/[0.18]">
          <AlertTriangle size={12} strokeWidth={2} className="text-red-500" />
          <span className="text-[10px] font-bold text-red-500 uppercase tracking-[0.08em]">Notice</span>
        </div>
      )}
      {content}
    </div>
  );
}