export const PRIORITY_DOT: Record<string, string> = {
  urgent: 'bg-red-500',
  high: 'bg-amber-500',
  medium: 'bg-blue-500',
  normal: 'bg-blue-500',
  low: 'bg-muted-foreground',
};

export const PRIORITY_CONFIG: Record<string, { badge: string; dot: string }> = {
  urgent: { badge: 'bg-red-50 text-red-700 border-red-100', dot: 'bg-red-500' },
  high: { badge: 'bg-amber-50 text-amber-700 border-amber-100', dot: 'bg-amber-500' },
  medium: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  normal: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  low: { badge: 'bg-muted text-muted-foreground border-border', dot: 'bg-muted-foreground' },
};

export function priorityConfig(p: string) {
  return PRIORITY_CONFIG[p?.toLowerCase()] ?? PRIORITY_CONFIG.normal;
}