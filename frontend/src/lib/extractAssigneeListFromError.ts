export function extractAssigneeListFromError(message: string): string[] {
  const match = message.match(/\[([^\]]+)\]/);
  if (!match) return [message];
  return match[1]
    .split(',')
    .map(s => s.trim().replace(/^['"]|['"]$/g, ''))
    .filter(Boolean);
}