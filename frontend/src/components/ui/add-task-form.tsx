import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { ClickUpListMetadata, VerifiedTask } from '@/api/api';
import { VerifiedTaskActionEnum } from '@/api/api';
import { EditableField } from './editable-field';
import { AssigneeField } from './assignee-field';
import { LocationField } from './location-field';
import { StatusField } from './status-field';
import { PriorityField } from './priority-field';
import { useClickUpStructure } from '@/hooks/clickup-structure-hooks/use-clikcup-structure';
import { CreateListForm } from './create-list-form';
import { AddStatusForm } from './add-status-from';

const EMPTY_TASK: VerifiedTask = {
  action: VerifiedTaskActionEnum.Create,
  task_name: '',
  task_description: '',
  task_assigne: '',
  task_status: '',
  task_priority: '',
  location: '',
};

interface Props {
  onAdd: (t: VerifiedTask) => void;
  onCancel: () => void;
  spaceId: string;
}

export function AddTaskForm({ onAdd, onCancel, spaceId }: Props) {
  const [draft, setDraft] = useState<VerifiedTask>(EMPTY_TASK);
  const [currentStatuses, setCurrentStatuses] = useState<string[]>([]);
  const [currentPriorities, setCurrentPriorities] = useState<string[]>([]);
  const [showAddList, setShowAddList] = useState(false);
  const [showAddStatus, setShowAddStatus] = useState(false);

  const { structure, loading: structureLoading, } = useClickUpStructure(spaceId);

  const set = (key: keyof VerifiedTask) => (value: string) =>
    setDraft(prev => ({ ...prev, [key]: value }));

  const handleLocationChange = (label: string, statuses: string[], priorities: string[]) => {
    setDraft(prev => ({
      ...prev,
      location: label,
      task_status: statuses[0] ?? '',
      task_priority: 'normal',
    }));
    setCurrentStatuses(statuses);
    setCurrentPriorities(priorities);
  };

  const handleListCreated = (list: ClickUpListMetadata) => {
    const label = list.name; 
    const statuses = list.statuses ?? [];
    const priorities = list.priorities ?? [];
    handleLocationChange(label, statuses, priorities);
    setShowAddList(false);
  }

  const locationNotSelected = !draft.location;

  return (
    <>
      <div className="border border-ring rounded-xl px-4 py-3.5 space-y-3 bg-card">
        <p className="text-xs font-medium text-muted-foreground">New task</p>

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
          <div className="col-span-2">
            <p className="text-xs text-muted-foreground mb-1">Assignees</p>
            <AssigneeField
              value={draft.task_assigne}
              onChange={set('task_assigne')}
            />
          </div>

          <div className="col-span-2">
            <p className="text-xs text-muted-foreground mb-1">Location</p>
            <LocationField
              value={draft.location}
              onChange={handleLocationChange}
              structure={structure}
              structureLoading={structureLoading}
              spaceId={spaceId}
              onRequestAddList={() => setShowAddList(true)}
            />
          </div>

          <div>
            <p className="text-xs text-muted-foreground mb-1">Status</p>
            <StatusField
              value={draft.task_status}
              onChange={set('task_status')}
              statuses={currentStatuses}
              disabled={locationNotSelected}
              structureLoading={structureLoading}
              structure={structure}
              onRequestAddStatus={() => setShowAddStatus(true)}
            />
          </div>

          <div>
            <p className="text-xs text-muted-foreground mb-1">Priority</p>
            <PriorityField
              value={draft.task_priority}
              onChange={set('task_priority')}
              priorities={currentPriorities}
              disabled={locationNotSelected}
              structure={structure}
              structureLoading={structureLoading}
            />
          </div>
        </div>

        {locationNotSelected && (
          <p className="text-xs text-muted-foreground/70 italic">
            Select a location to enable status and priority
          </p>
        )}

        <div className="flex justify-end gap-2 pt-1">
          <Button variant="outline" size="sm" onClick={onCancel}>
            Cancel
          </Button>
          <Button 
            onClick={() => { if (draft.task_name.trim()) onAdd(draft); }}
            disabled={!draft.task_name.trim()}
            className="gap-2"
          >
            <Plus className="w-4 h-4" />
            Add task
          </Button>
        </div>
      </div>

      <CreateListForm
        isOpen={showAddList}
        onClose={() => setShowAddList(false)}
        onSuccess={handleListCreated} 
        spaceId={spaceId}
      />

      <AddStatusForm
        isOpen={showAddStatus}
        spaceId={spaceId}
        listId={draft.location}
        onClose={() => setShowAddStatus(false)}
        onSuccess={(updatedList: ClickUpListMetadata, addedStatus: string) => {
          if (updatedList.statuses) {
            setCurrentStatuses(updatedList.statuses);
            setDraft(prev => ({
              ...prev,
              task_status: addedStatus,
            }));
          }
          setShowAddStatus(false);
        }}
      />
    </>
  );
}