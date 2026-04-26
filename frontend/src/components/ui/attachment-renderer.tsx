import { ShieldCheck } from "lucide-react";
import { MarketCard } from "./market-card";
import { BacklogCard } from "./backlog-card";
import { SprintCard } from "./sprint-card";
import type { UiSprint } from "@/types/backlog";

export function AttachmentRenderer({ attachment, onMarketSubmit, onBacklogSubmit }: any) {
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

  return null;
}