export function TaskSkeleton() {
  return (
    <div className="border border-border rounded-xl px-4 py-3.5 space-y-2 animate-pulse">
      <div className="flex items-start gap-3">
        <div className="w-2 h-2 mt-[7px] rounded-full bg-muted flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-4 w-48 bg-muted rounded" />
          <div className="h-3 w-64 bg-muted rounded" />
          <div className="h-3 w-40 bg-muted rounded" />
          <div className="flex gap-2 mt-2">
            <div className="h-5 w-16 bg-muted rounded-md" />
            <div className="h-5 w-16 bg-muted rounded-md" />
          </div>
        </div>
        <div className="flex gap-1">
          <div className="w-7 h-7 bg-muted rounded" />
          <div className="w-7 h-7 bg-muted rounded" />
        </div>
      </div>
    </div>
  );
}