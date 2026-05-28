import { ShieldCheck } from "lucide-react";
import { MarketCard } from "./market-card";
import { BacklogCard } from "./backlog-card";
import { SprintCard } from "./sprint-card";
import type { UiSprint } from "@/types/backlog";

export function AttachmentRenderer({ 
  attachment, 
  onMarketSubmit, 
  onBacklogSubmit ,
  onClickUpYes,
  onClickUpNo,
}: any) {
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
            : attachment.mode === "validation"
            ? "Submitted for validation"
            : attachment.mode === "backlog_refinement"
            ? "Submitted for refinement"
            : "Submitted for finishing"}
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

  if (attachment.type === "clickup_prompt") {
    return (
      <div className="mt-3 px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl flex flex-col gap-3">
        <p className="text-[13px] text-slate-700 leading-relaxed">
          Would you like to save this sprint backlog as tasks in your ClickUp space?
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => onClickUpYes?.(attachment.data)}
            className="px-4 py-1.5 text-[12px] font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-700 transition-colors cursor-pointer"
          >
            Yes
          </button>
          <button
            onClick={() => onClickUpNo?.()}
            className="px-4 py-1.5 text-[12px] font-medium bg-white text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
          >
            No
          </button>
        </div>
      </div>
    );
  }

  return null;
}