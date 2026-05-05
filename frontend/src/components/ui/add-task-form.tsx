import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { VerifiedTask } from '@/api/api';
import { VerifiedTaskActionEnum } from '@/api/api';
import { EditableField } from './editable-field';
import { AssigneeField } from './assignee-field';


const PRIORITIES = ['urgent', 'high', 'normal', 'low'];
const STATUSES = ['To Do', 'In Progress', 'In Review', 'Done'];

const EMPTY_TASK: VerifiedTask = {
  action: VerifiedTaskActionEnum.Create,
  task_name: '',
  task_description: '',
  task_assigne: '',
  task_status: 'To Do',
  task_priority: 'normal',
  location: '',
};


export function AddTaskForm({
  onAdd,
  onCancel,
}: {
  onAdd: (t: VerifiedTask) => void;
  onCancel: () => void;
}) {
  const [draft, setDraft] = useState<VerifiedTask>(EMPTY_TASK);

  const set = (key: keyof VerifiedTask) => (value: string) =>
    setDraft(prev => ({ ...prev, [key]: value }));

  return (
    <div className="border border-ring rounded-xl px-4 py-3.5 space-y-3 bg-card">
      <p className="text-xs font-medium text-muted-foreground">
        New task
      </p>

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
          value={draft.location}
          onChange={set('location')}
          placeholder="Location"
        />

        <EditableField
          value={draft.task_status}
          onChange={set('task_status')}
          type="select"
          options={STATUSES}
        />

        <EditableField
          value={draft.task_priority}
          onChange={set('task_priority')}
          type="select"
          options={PRIORITIES}
        />
      </div>

      <div className="flex justify-end gap-2 pt-1">
        <Button variant="outline" size="sm" onClick={onCancel}>
          Cancel
        </Button>

        <Button
          size="sm"
          onClick={() => {
            if (draft.task_name.trim()) onAdd(draft);
          }}
          disabled={!draft.task_name.trim()}
          className="gap-1"
        >
          <Plus className="w-3.5 h-3.5" />
          Add task
        </Button>
      </div>
    </div>
  );
}