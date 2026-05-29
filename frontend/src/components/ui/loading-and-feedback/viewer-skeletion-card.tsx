import { TaskSkeleton } from "./task-skeleton";

export function ViewerSkeleton() {
  return (
    <div className="space-y-3">
      <div className="h-9 w-full rounded-md bg-muted animate-pulse" />
      {Array.from({ length: 3 }).map((_, i) => (
        <TaskSkeleton key={i} />
      ))}
    </div>
  );
}