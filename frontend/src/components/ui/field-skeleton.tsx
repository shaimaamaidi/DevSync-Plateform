export function FieldSkeleton() {
  return (
    <div className="space-y-1.5">
      <div className="h-3 w-20 rounded bg-muted animate-pulse" />
      <div className="h-11 w-full rounded-lg bg-muted animate-pulse" />
    </div>
  );
}