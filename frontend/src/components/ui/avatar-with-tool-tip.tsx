import { useState } from "react";

interface AvatarWithTooltipProps {
  mail: string;
  name: string;
  className?: string;
}

export function AvatarWithTooltip({ mail, name, className = "" }: AvatarWithTooltipProps) {
  const [visible, setVisible] = useState(false);

  return (
    <span
      className="relative"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      <span
        className={`w-4 h-4 rounded-full bg-primary/15 text-primary flex items-center justify-center text-[10px] font-semibold border border-background cursor-default ${className}`}
      >
        {name[0].toUpperCase()}
      </span>
      {visible && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 z-[100] flex flex-col items-center pointer-events-none">
          <span className="bg-popover border border-border rounded-md shadow-md px-2 py-1 whitespace-nowrap">
            <span className="block text-xs font-medium text-foreground">{name}</span>
            <span className="block text-[10px] text-muted-foreground">{mail}</span>
          </span>
          <span className="w-2 h-2 bg-popover border-r border-b border-border rotate-45 -mt-1" />
        </span>
      )}
    </span>
  );
}