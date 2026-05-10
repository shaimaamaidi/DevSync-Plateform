import { useState, useRef, useEffect } from 'react';
import { Trash2, Pen, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { VerifiedTask, FolderWithListsMetadata, ClickUpListMetadata } from '@/api/api';
import { VerifiedTaskActionEnum } from '@/api/api';
import { EditableField } from './editable-field';
import { AssigneeField } from './assignee-field';
import { LocationField } from './location-field';
import { StatusField } from './status-field';
import { PriorityField } from './priority-field';
import { AddStatusForm } from './add-status-from';
import { CreateListForm } from './create-list-form';
import { buildLocationOptions } from './location-field';
import { AssigneeAvatars } from './assignees-avatar';

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

interface Props {
  task: VerifiedTask;
  onDelete: () => void;
  onUpdate: (updated: VerifiedTask) => void;
  priorityConfig: (priority: string) => { badge: string; dot: string };
  structure: FolderWithListsMetadata[];
  structureLoading: boolean;
  spaceId: string;
}

export function VerifiedTaskCard({
  task,
  onDelete,
  onUpdate,
  priorityConfig,
  structure,
  structureLoading,
  spaceId,
}: Props) {
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<VerifiedTask>(task);
  const [currentStatuses, setCurrentStatuses] = useState<string[]>([]);
  const [currentPriorities, setCurrentPriorities] = useState<string[]>([]);
  const [showAddStatus, setShowAddStatus] = useState(false);
  const [showAddList, setShowAddList] = useState(false);

  const [locationOpen, setLocationOpen] = useState(false);
  const locationRef = useRef<HTMLDivElement>(null);
  const options = buildLocationOptions(structure);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (locationRef.current && !locationRef.current.contains(e.target as Node))
        setLocationOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const cfg = priorityConfig(task.task_priority);

  const set = (key: keyof VerifiedTask) => (value: string) =>
    setDraft(prev => ({ ...prev, [key]: value }));

  const handleLocationChange = (
    label: string,
    statuses: string[],
    priorities: string[],
  ) => {
    setDraft(prev => ({
      ...prev,
      location: label,
    }));
    setCurrentStatuses(statuses);
    setCurrentPriorities(priorities);
  };

  const handleListCreated = (list: ClickUpListMetadata) => {
    const label = list.name;
    const statuses = list.statuses ?? [];
    const priorities = list.priorities ?? [];
    setDraft(prev => ({
      ...prev,
      location: label,  
    }));
    setCurrentStatuses(statuses);
    setCurrentPriorities(priorities);
    setShowAddList(false);

    if (!editing) {
      onUpdate({ ...task, location: label });
    }
  };

  const locationNotSelected = !draft.location;

  return (
    <>
      <div
        className={`border rounded-xl px-4 py-3.5 transition-colors ${
          editing ? 'border-ring' : 'border-border/60 hover:border-border'
        }`}
      >
        {editing ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <ActionBadge action={task.action} taskId={task.task_id} />
              <span className="text-xs text-muted-foreground ml-auto">editing</span>
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
              <Button
                variant="outline"
                size="sm"
                onClick={() => { setDraft(task); setEditing(false); }}
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={() => { onUpdate(draft); setEditing(false); }}
              >
                Save
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-3">
            <div className={`w-2 h-2 mt-[7px] rounded-full flex-shrink-0 ${cfg.dot}`} />

            <div className="flex-1 min-w-0" onClick={() => setExpanded(p => !p)}>
              <div className="flex items-center gap-2 flex-wrap">
                <p className="text-sm font-medium">{task.task_name}</p>
                <ActionBadge action={task.action} taskId={task.task_id} />
              </div>

              <p className={`text-sm text-muted-foreground mt-1 ${expanded ? '' : 'line-clamp-2'}`}>
                {task.task_description}
              </p>

              <div className="flex items-center gap-3 mt-3 flex-wrap">
                <AssigneeAvatars value={task.task_assigne} />

                <span className={`text-xs px-2 py-0.5 rounded-md border ${cfg.badge}`}>
                  {task.task_priority}
                </span>
                <span className="text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground">
                  {task.task_status}
                </span>

                <div ref={locationRef} className="relative" onClick={e => e.stopPropagation()}>
                  <button
                    type="button"
                    onClick={() => setLocationOpen(p => !p)}
                    className={`text-xs px-2 py-0.5 rounded-md border transition-colors ${
                      task.location?.trim()
                        ? 'bg-muted/50 text-muted-foreground border-border hover:border-primary/40'
                        : 'bg-amber-50 text-amber-700 border-amber-200 hover:border-amber-400'
                    }`}
                  >
                    {task.location?.trim() || '⚠ No location'}
                  </button>

                  {locationOpen && (
                    <div className="absolute z-50 mt-1 left-0 w-56 bg-popover border border-border rounded-md shadow-md max-h-52 overflow-y-auto">
                      {structureLoading ? (
                        <div className="px-3 py-2 text-xs text-muted-foreground">Loading…</div>
                      ) : options.length === 0 ? (
                        <div className="px-3 py-2 text-xs text-muted-foreground italic cursor-default">
                          {structure.length > 0 ? 'no list available' : 'no folder and no list available'}
                        </div>
                      ) : (
                        options.map(opt => (
                          <button
                            key={opt.listId}
                            type="button"
                            onClick={() => {
                              onUpdate({ ...task, location: opt.label });
                              setLocationOpen(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors ${
                              task.location === opt.label ? 'bg-muted font-medium' : ''
                            }`}
                          >
                            {opt.label}
                          </button>
                        ))
                      )}
                      <div className="border-t border-border">
                        <button
                          type="button"
                          onClick={() => { setLocationOpen(false); setShowAddList(true); }}
                          className="w-full text-left flex items-center gap-2 px-3 py-2 text-sm text-primary hover:bg-primary/5 font-medium"
                        >
                          <Plus className="w-3.5 h-3.5" />
                          Create new list…
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-gray-500 hover:text-gray-700"
                onClick={() => setEditing(true)}
              >
                <Pen className="w-3.5 h-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-destructive"
                onClick={onDelete}
              >
                <Trash2 className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        )}
      </div>

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

      <CreateListForm
        isOpen={showAddList}
        onClose={() => setShowAddList(false)}
        onSuccess={handleListCreated} 
        spaceId={spaceId}
      />
    </>
  );
}