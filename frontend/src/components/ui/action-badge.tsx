import { VerifiedTaskFromSummaryActionEnum } from "@/api/api";

export function ActionBadge({
  action,
  taskId,
}: {
  action: VerifiedTaskFromSummaryActionEnum;
  taskId?: string | null;
}) {
  if (action === VerifiedTaskFromSummaryActionEnum.Create) {
    return (
      <span className="text-xs px-2 py-0.5 rounded-md border bg-green-50 text-green-700 border-green-100 font-medium">
        create
      </span>
    );
  }
  return (
    <span className="text-xs px-2 py-0.5 rounded-md border bg-amber-50 text-amber-700 border-amber-100 font-medium">
      update {taskId ? `#${taskId}` : ''}
    </span>
  );
}