import { useState } from 'react';
import { Trash2, ChevronDown, GripVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { GeneratedTask } from '@/api/api';
import { AssigneeAvatars } from '../ui/assignees-avatar';

const PRIORITY_CONFIG: Record<string, { badge: string; dot: string }> = {
  urgent: { badge: 'bg-red-50 text-red-700 border-red-100', dot: 'bg-red-500' },
  high: { badge: 'bg-amber-50 text-amber-700 border-amber-100', dot: 'bg-amber-500' },
  medium: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  normal: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  low: { badge: 'bg-muted text-muted-foreground border-border', dot: 'bg-muted-foreground' },
};

function priorityConfig(p: string) {
  return PRIORITY_CONFIG[p?.toLowerCase()] ?? PRIORITY_CONFIG['normal'];
}

interface Props {
  task: GeneratedTask;
  onDelete: () => void;
}

export function GeneratedTaskCard({ task, onDelete }: Props) {
  const [expanded, setExpanded] = useState(false);
  const cfg = priorityConfig(task.task_priority);

  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData(
      'application/x-generated-task',
      JSON.stringify(task)
    );
    e.dataTransfer.effectAllowed = 'copy';
  };

  return (
    <div
      draggable
      onDragStart={handleDragStart}
      className="bg-card border border-border/60 rounded-xl px-4 py-3.5 hover:border-border transition-colors cursor-grab active:cursor-grabbing group"
    >
      <div className="flex items-start gap-3">
        <GripVertical className="w-4 h-4 text-muted-foreground/40 group-hover:text-muted-foreground flex-shrink-0 mt-[3px]" />

        <div className={`w-2 h-2 rounded-full mt-[7px] ${cfg.dot}`} />

        <div className="flex-1 min-w-0" onClick={() => setExpanded(p => !p)}>
          <p className="text-sm font-medium">{task.task_name}</p>

          <p
            className={`text-sm text-muted-foreground mt-1 ${
              expanded ? '' : 'line-clamp-2'
            }`}
          >
            {task.task_description}
          </p>

          <div className="flex items-center gap-3 mt-3 flex-wrap">
            <AssigneeAvatars value={task.task_assigne} />

            <span className={`text-xs px-2 py-0.5 rounded-md border ${cfg.badge}`}>
              {task.task_priority}
            </span>

            <span className="text-xs px-2 py-0.5 rounded-md border bg-muted">
              {task.task_status}
            </span>

            <span className="text-xs px-2 py-0.5 rounded-md border bg-muted/50">
              {task.folder}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            onClick={e => {
              e.stopPropagation();
              onDelete();
            }}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </Button>

          <ChevronDown
            className={`w-4 h-4 cursor-pointer transition-transform ${
              expanded ? 'rotate-180' : ''
            }`}
            onClick={() => setExpanded(p => !p)}
          />
        </div>
      </div>
    </div>
  );
}