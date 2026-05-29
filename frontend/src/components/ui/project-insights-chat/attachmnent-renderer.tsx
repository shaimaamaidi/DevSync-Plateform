import type { InsightsChatAttachment } from "@/types/insights-chat";
import { CommitTraceResult } from "./commit-tracer-result";
import { ProjectStatusResult } from "./project-status-result";
import { TaskConfirmSingle } from "./task-confirm-single";
import { TaskSelectMultiple } from "./task-select-multiple";
import { TaskSynthesisResult } from "./task-synthesis-result";
import { WeeklySummaryResult } from "./weekly-summary-result";

export function AttachmentRenderer({ attachment, onAction }: { attachment: InsightsChatAttachment; onAction?: (a: string, p?: any) => void }) {
  switch (attachment.type) {
    case "task_confirm_single": return <TaskConfirmSingle data={attachment.data} onAction={onAction} />;
    case "task_select_multiple": return <TaskSelectMultiple data={attachment.data} onAction={onAction} />;
    case "task_synthesis_result": return <TaskSynthesisResult data={attachment.data} />;
    case "project_status_result": return <ProjectStatusResult data={attachment.data} />;
    case "weekly_summary_result": return <WeeklySummaryResult data={attachment.data} />;
    case "commit_trace_result": return <CommitTraceResult data={attachment.data} />;
    default: return null;
  }
}
