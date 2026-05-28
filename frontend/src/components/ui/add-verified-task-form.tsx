import { useState } from 'react';
import { AlertCircle, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { ClickUpListMetadata, VerifiedTaskFromSummary } from '@/api/api';
import { VerifiedTaskFromSummaryActionEnum } from '@/api/api';
import { EditableField } from './editable-field';
import { AssigneeField } from './assignee-field';
import { LocationField } from './location-field';
import { StatusField } from './status-field';
import { PriorityField } from './priority-field';
import { useClickUpStructure } from '@/hooks/clickup-structure-hooks/use-clikcup-structure';
import { CreateListForm } from './create-list-form';
import { AddStatusForm } from './add-status-from';
import { createPortal } from 'react-dom';

const EMPTY_TASK: VerifiedTaskFromSummary = {
  action: VerifiedTaskFromSummaryActionEnum.Create,
  task_name: '',
  task_description: '',
  task_assigne: '',
  task_status: '',
  task_priority: '',
  location: '',
};

interface Props {
  isOpen: boolean;
  onAdd: (t: VerifiedTaskFromSummary) => void;
  onCancel: () => void;
  spaceId: string;
}

export function AddVerifiedTaskForm({ isOpen, onAdd, onCancel, spaceId }: Props) {
  const { structure, loading: structureLoading } = useClickUpStructure(spaceId);

  const [draft, setDraft] = useState<VerifiedTaskFromSummary>(EMPTY_TASK);
  const [currentStatuses, setCurrentStatuses] = useState<string[]>([]);
  const [currentPriorities, setCurrentPriorities] = useState<string[]>([]);
  const locationNotSelected = !draft.location;

  const [showAddList, setShowAddList] = useState(false);
  const [showAddStatus, setShowAddStatus] = useState(false);

  const [errors, setErrors] = useState<Record<string, string>>({});

  const set = (key: keyof VerifiedTaskFromSummary) => (value: string) =>
    setDraft(prev => ({ ...prev, [key]: value }));

  const validate = (): boolean => {
    setErrors({});
    const newErrors: Record<string, string> = {};

    if (!draft.task_name.trim()) newErrors.task_name = 'Task name is required';
    if (!draft.task_description.trim()) newErrors.task_description = 'Description is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

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
  };

  if (!isOpen)
    return null;

  return (
    <>
      <div className="border border-ring rounded-xl bg-card flex flex-col max-h-[70vh]">

        <div className="px-3 sm:px-4 pt-3 sm:pt-3.5 pb-2 shrink-0">
          <p className="text-xs font-medium text-muted-foreground">New task</p>
        </div>

        <div className="space-y-3 px-3 sm:px-4 py-2 overflow-y-auto flex-1">
          <div className="space-y-1">
            <EditableField
              value={draft.task_name}
              onChange={set('task_name')}
              placeholder="Task name"
              className="font-medium"
            />
            {errors.task_name && (
              <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {errors.task_name}
              </div>
            )}
          </div>

          <div className="space-y-1">
            <EditableField
              value={draft.task_description}
              onChange={set('task_description')}
              type="textarea"
              placeholder="Description"
            />
            {errors.task_description && (
              <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {errors.task_description}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div className="col-span-1 sm:col-span-2">
              <p className="text-xs text-muted-foreground mb-1">Assignees</p>
              <AssigneeField
                value={draft.task_assigne}
                onChange={set('task_assigne')}
              />
            </div>

            <div className="col-span-1 sm:col-span-2">
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
        </div>

        <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 px-3 sm:px-4 pb-3 sm:pb-3.5 pt-3 border-t border-border shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={onCancel}
            className="w-full sm:w-auto"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              if (validate()) {
                onAdd(draft);
              }
            }}
            disabled={!draft.task_name.trim()}
            className="gap-2 w-full sm:w-auto"
          >
            <Plus className="w-4 h-4" />
            Add task
          </Button>
        </div>
      </div>

      {showAddList && createPortal(
        <CreateListForm
          isOpen={showAddList}
          onClose={() => setShowAddList(false)}
          onSuccess={handleListCreated}
          spaceId={spaceId}
        />,
        document.body
      )}

      {showAddStatus && createPortal(
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
        />,
        document.body
      )}
    </>
  );
}