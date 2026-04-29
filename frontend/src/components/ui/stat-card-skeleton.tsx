import { Card } from "./card";


interface statConfigs{
    icon: React.ComponentType<{ className?: string }>;
    iconBg: string;
    iconColor: string;
}

export function StatCardSkeleton({ icon: Icon, iconBg, iconColor }:  statConfigs) {
  return (
    <Card className="p-6 border-border">
      <div className="flex items-center justify-between">
        <div className="flex flex-col justify-between min-h-[88px]">
          <div className="h-4 w-32 rounded bg-muted animate-pulse" />
          <div className="h-8 w-16 rounded bg-muted animate-pulse mt-2" />
          <div className="h-3 w-24 rounded bg-muted animate-pulse mt-2" />
        </div>
        <div className={`p-3 ${iconBg} rounded-lg`}>
          <Icon className={`w-6 h-6 ${iconColor} opacity-40`} />
        </div>
      </div>
    </Card>
  );
}