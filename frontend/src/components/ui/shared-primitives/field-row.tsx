interface FieldRowProps {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}

export function FieldRow({ icon, label, value }: FieldRowProps) {
  return (
    <div className="flex items-start gap-3 py-3 border-b border-border last:border-0">
      <span className="mt-0.5 text-muted-foreground flex-shrink-0">{icon}</span>
      <div className="flex flex-col gap-0.5 min-w-0">
        <span className="text-[11px] text-muted-foreground uppercase tracking-wide font-medium">{label}</span>
        <span className="text-sm font-medium text-foreground break-all">{value}</span>
      </div>
    </div>
  );
}