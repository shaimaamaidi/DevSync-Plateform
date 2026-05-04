import { useState } from 'react';
import { Trash2, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { VerifiedTask } from '@/api/api';

import { VerifiedTaskActionEnum } from '@/api/api';
import { EditableField } from './editable-field';
import { AssigneeField } from './assignee-field';

function ActionBadge({
  action,
  taskId,
}: {
  action: VerifiedTaskActionEnum;
  taskId?: string | null;
}) {
  if (action === VerifiedTaskActionEnum.Create) {
    return (
      <span className="text-xs px-2 py-0.5 rounded-md border bg-green-50 text-green-700 border-green-100 font-medium">
        create
      </span>
    );
  }

  return (
    <span className="text-xs px-2 py-0.5 rounded-md border bg-amber-50 text-amber-700 border-amber-100 font-medium">
      update {taskId ? `#${taskId}` : ''}
    </span>
  );
}


export function VerifiedTaskCard({
  task,
  onDelete,
  onUpdate,
  priorityConfig,
}: {
  task: VerifiedTask;
  onDelete: () => void;
  onUpdate: (t: VerifiedTask) => void;
  priorityConfig: (priority: string) => { badge: string; dot: string };
}) {
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState(false);

  const cfg = priorityConfig(task.task_priority);
  const [draft, setDraft] = useState<VerifiedTask>(task);

  const set = (key: keyof VerifiedTask) => (value: string) =>
    setDraft(prev => ({ ...prev, [key]: value }));

  /* ───────────────────────────────────────────────────────── */

  return (
    <div
      className={`border rounded-xl px-4 py-3.5 transition-colors ${
        editing
          ? 'border-ring'
          : 'border-border/60 hover:border-border'
      }`}
    >
      {/* ───────── EDIT MODE ───────── */}
      {editing ? (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <ActionBadge action={task.action} taskId={task.task_id} />
            <span className="text-xs text-muted-foreground ml-auto">
              editing
            </span>
          </div>

          <EditableField
            value={draft.task_name}
            onChange={set('task_name')}
            placeholder="Task name"
            className="font-medium"
          />

          <EditableField
            value={draft.task_description}
            onChange={set('task_description')}
            type="textarea"
            placeholder="Description"
          />

          <div className="grid grid-cols-2 gap-2">
            <AssigneeField
              value={draft.task_assigne}
              onChange={set('task_assigne')}
            />

            <EditableField
              value={draft.folder}
              onChange={set('folder')}
              placeholder="Folder"
            />

            <EditableField
              value={draft.task_status}
              onChange={set('task_status')}
              type="select"
              options={['To Do', 'In Progress', 'In Review', 'Done']}
            />

            <EditableField
              value={draft.task_priority}
              onChange={set('task_priority')}
              type="select"
              options={['urgent', 'high', 'normal', 'low']}
            />
          </div>

          <div className="flex justify-end gap-2 pt-1">
            <Button variant="outline" size="sm" onClick={() => setEditing(false)}>
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={() => {
                onUpdate(draft);
                setEditing(false);
              }}
            >
              Save
            </Button>
          </div>
        </div>
      ) : (
        /* ───────── VIEW MODE ───────── */
        <div className="flex items-start gap-3">
          <div className={`w-2 h-2 mt-[7px] rounded-full ${cfg.dot}`} />

          <div
            className="flex-1 min-w-0"
            onClick={() => setExpanded(p => !p)}
          >
            <div className="flex items-center gap-2 flex-wrap">
              <p className="text-sm font-medium">{task.task_name}</p>

              <ActionBadge
                action={task.action}
                taskId={task.task_id}
              />
            </div>

            <p
              className={`text-sm text-muted-foreground mt-1 ${
                expanded ? '' : 'line-clamp-2'
              }`}
            >
              {task.task_description}
            </p>

            <div className="flex items-center gap-3 mt-3 flex-wrap">
              <span className={`text-xs px-2 py-0.5 rounded-md border ${cfg.badge}`}>
                {task.task_priority}
              </span>

              <span className="text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground">
                {task.task_status}
              </span>

              <span className="text-xs px-2 py-0.5 rounded-md border bg-muted/50 text-muted-foreground">
                {task.folder}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0"
              onClick={() => setEditing(true)}
            >
              ✏️
            </Button>

            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0 text-destructive"
              onClick={onDelete}
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
      )}
    </div>
  );
}