import { getToolLabel } from "@/lib/tool-labels";

interface TypingIndicatorProps {
  toolName?: string | null; 
}

export function BacklogTypingIndicator({ toolName }: TypingIndicatorProps) {
  return (
    <div className="flex items-center gap-[5px] py-[3px]">
       {toolName && ( 
        <span className="mr-2 text-[12px] text-slate-400 italic">
          {getToolLabel(toolName)}
        </span>
      )}
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="w-[7px] h-[7px] rounded-full bg-slate-300 animate-bounce"
          style={{ animationDelay: `${i * 0.18}s` }}
        />
      ))}

    </div>
  );
}