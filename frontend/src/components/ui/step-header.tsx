export function StepHeader({
  number,
  isLoading,
  title,
  subtitle,
}: {
  number: number;
  isLoading?: boolean;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className={`flex gap-3 ${subtitle ? "items-start" : "items-center"}`}>
      <div className="w-7 h-7 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold flex-shrink-0">
        {number}
      </div>
      <div>
        <h2 className="text-base font-semibold text-foreground">{title}</h2>
        {isLoading ? (
          <div className="flex gap-1 mt-1">
            <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:0ms]" />
            <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:200ms]" />
            <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:400ms]" />
          </div>
        ) : (
          subtitle && (
            <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>
          )
        )}
      </div>
    </div>
  );
}