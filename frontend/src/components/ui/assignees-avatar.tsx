// task_assigne is a comma-separated string of member names.
// The special value "غير محدد" means no assignees.

export const UNASSIGNED = 'غير محدد';

const AVATAR_COLORS = [
  'bg-blue-100 text-blue-800',
  'bg-green-100 text-green-800',
  'bg-pink-100 text-pink-800',
  'bg-purple-100 text-purple-800',
  'bg-orange-100 text-orange-800',
];

function getInitials(name: string) {
  return name
    .trim()
    .split(' ')
    .map(w => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

export function parseAssignees(value: string): string[] {
  if (!value || value.trim() === UNASSIGNED) return [];
  return value.split(',').map(s => s.trim()).filter(Boolean);
}

export function AssigneeAvatars({ value }: { value: string }) {
  const names = parseAssignees(value);

  if (names.length === 0) {
    return <span className="text-xs text-muted-foreground italic">Unassigned</span>;
  }

  const shown = names.slice(0, 3);
  const extra = names.length - shown.length;

  return (
    <div className="flex items-center gap-1.5">
      <div className="flex -space-x-1.5">
        {shown.map((name, i) => {
          const initials = getInitials(name);
          const color = AVATAR_COLORS[initials.charCodeAt(0) % AVATAR_COLORS.length];
          return (
            <div
              key={i}
              title={name}
              className={`w-6 h-6 rounded-full border-2 border-background flex items-center justify-center text-[10px] font-semibold ${color}`}
            >
              {initials}
            </div>
          );
        })}
        {extra > 0 && (
          <div className="w-6 h-6 rounded-full border-2 border-background bg-muted text-muted-foreground flex items-center justify-center text-[10px] font-semibold">
            +{extra}
          </div>
        )}
      </div>
      <span className="text-xs text-muted-foreground">
        {shown.join(', ')}{extra > 0 ? ` +${extra}` : ''}
      </span>
    </div>
  );
}