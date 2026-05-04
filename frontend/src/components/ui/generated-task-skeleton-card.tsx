export function GeneratedTaskSkeletonCard() {
  return (
    <div className="bg-card border border-border/60 rounded-xl px-4 py-3.5 animate-pulse">
      <div className="flex items-start gap-3">
        <div className="w-4 h-4 rounded bg-muted mt-1 flex-shrink-0" />
        <div className="w-2 h-2 rounded-full bg-muted mt-2 flex-shrink-0" />

        <div className="flex-1 space-y-2">
          <div className="h-4 w-2/3 rounded bg-muted" />
          <div className="h-3 w-full rounded bg-muted" />
          <div className="h-3 w-4/5 rounded bg-muted" />

          <div className="flex gap-2 mt-3">
            <div className="h-5 w-16 rounded-full bg-muted" />
            <div className="h-5 w-14 rounded-md bg-muted" />
            <div className="h-5 w-14 rounded-md bg-muted" />
          </div>
        </div>
      </div>
    </div>
  );
}