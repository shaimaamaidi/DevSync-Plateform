import type { ClickUpListMetadata, ClickUpTask, FolderWithListsMetadata, MemberDTO, UpdateTaskRequest } from "@/api/api";
import { AddStatusForm } from "./add-status-from";
import { Loader2, Pen, Trash2 } from "lucide-react";
import { Button } from "./button";
import { PriorityField } from "./priority-field";
import { StatusField } from "./status-field";
import { AssigneeSelect } from "./assignee-select";
import { EditableField } from "./editable-field";
import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "./dialog";
import type { TaskDraft } from "@/types/clickup";
import { priorityConfig } from "@/lib/priority";
import { AssigneeBadges } from "./assignee-badge";

interface TaskCardProps {
  task: ClickUpTask;
  statuses: string[];
  priorities: string[];
  structureForFields: FolderWithListsMetadata[];
  structureLoading: boolean;
  listId: string;
  spaceId: string;
  members: MemberDTO[];
  membersLoading: boolean;
  onDelete: () => void;
  onSave: (req: Omit<UpdateTaskRequest, 'task_id' | 'space_id'>) => Promise<void>;
  busy: boolean;
}

export function parseAssignees(raw: string | null | undefined): string[] {
  return raw ? raw.split(',').map((s) => s.trim()).filter(Boolean) : [];
}

function buildInitialDraft(task: ClickUpTask): TaskDraft {
  return {
    name: task.name,
    description: task.description,
    status: task.status,
    priority: task.priority ?? '',
    assignees: parseAssignees(task.assignee),
  };
}

function isDraftDirty(draft: TaskDraft, task: ClickUpTask): boolean {
  return (
    draft.name !== task.name ||
    draft.description !== task.description ||
    draft.status !== task.status ||
    draft.priority !== (task.priority ?? '') ||
    draft.assignees.join(',') !== parseAssignees(task.assignee).join(',')
  );
}

export function TaskCard({
  task,
  statuses,
  priorities,
  structureForFields,
  structureLoading,
  listId,
  spaceId,
  members,
  membersLoading,
  onDelete,
  onSave,
  busy,
}: TaskCardProps) {
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showAddStatus, setShowAddStatus] = useState(false);
  const [localStatuses, setLocalStatuses] = useState<string[]>(statuses);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ name?: string; description?: string }>({});

  const [draft, setDraft] = useState<TaskDraft>(() => buildInitialDraft(task));

  useEffect(() => setLocalStatuses(statuses), [statuses]);

  useEffect(() => {
    setDraft(buildInitialDraft(task));
  }, [task]);

  const set =
    <K extends keyof TaskDraft>(key: K) =>
    (value: TaskDraft[K]) => {
      setDraft((prev) => ({ ...prev, [key]: value }));
      if (key === 'name' || key === 'description') {
        setFieldErrors((prev) => ({ ...prev, [key]: undefined }));
      }
    };

  const validate = (): boolean => {
    const errors: { name?: string; description?: string } = {};
    if (!draft.name?.trim()) {
      errors.name = 'Task name cannot be empty.';
    }
    if (!draft.description?.trim()) {
      errors.description = 'Description cannot be empty.';
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const dirty = isDraftDirty(draft, task);
  const canSave = dirty && !saving && !busy;

  const handleSave = async () => {
    if (!validate()) return;
    setSaving(true);
    await onSave({
      name: draft.name,
      description: draft.description,
      status: draft.status,
      priority: draft.priority || null,
      assignees: draft.assignees.length > 0 ? draft.assignees.join(',') : null,
      old_assignees: task.assignee ?? null,
    });
    setSaving(false);
    setEditing(false);
  };

  const handleCancel = () => {
    setDraft(buildInitialDraft(task));
    setFieldErrors({});
    setEditing(false);
  };

  const cfg = priorityConfig(task.priority ?? '');

  const inputErrorClass = (hasError: boolean) =>
    hasError
      ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
      : '';

  return (
    <>
      <div
        className={`border rounded-xl px-4 py-3.5 transition-colors ${
          editing ? 'border-ring' : 'border-border/60 hover:border-border'
        }`}
      >
        {editing ? (
          <div className="space-y-3">
            <span className="text-xs text-muted-foreground">editing</span>

            <div className="space-y-1">
              <EditableField
                value={draft.name}
                onChange={(v) => set('name')(v)}
                placeholder="Task name"
                className={`font-medium ${inputErrorClass(!!fieldErrors.name)}`}
              />
              {fieldErrors.name && (
                <p className="text-destructive text-xs px-1">{fieldErrors.name}</p>
              )}
            </div>

            <div className="space-y-1">
              <EditableField
                value={draft.description}
                onChange={(v) => set('description')(v)}
                type="textarea"
                placeholder="Description"
                className={inputErrorClass(!!fieldErrors.description)}
              />
              {fieldErrors.description && (
                <p className="text-destructive text-xs px-1">{fieldErrors.description}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="col-span-2">
                <p className="text-xs text-muted-foreground mb-1">Assignees</p>
                <AssigneeSelect
                  value={draft.assignees}
                  onChange={set('assignees')}
                  members={members}
                  loading={membersLoading}
                  disabled={busy}
                />
              </div>

              <div>
                <p className="text-xs text-muted-foreground mb-1">Status</p>
                <StatusField
                  value={draft.status}
                  onChange={(v) => set('status')(v)}
                  statuses={localStatuses}
                  disabled={false}
                  structureLoading={structureLoading}
                  structure={structureForFields}
                  onRequestAddStatus={() => setShowAddStatus(true)}
                />
              </div>

              <div>
                <p className="text-xs text-muted-foreground mb-1">Priority</p>
                <PriorityField
                  value={draft.priority}
                  onChange={(v) => set('priority')(v)}
                  priorities={priorities}
                  disabled={false}
                  structure={structureForFields}
                  structureLoading={structureLoading}
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-1">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancel}
                disabled={saving || busy}
              >
                Cancel
              </Button>
              <Button size="sm" onClick={handleSave} disabled={!canSave}>
                {saving && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
                Save
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-3">
            <div className={`w-2 h-2 mt-[7px] rounded-full flex-shrink-0 ${cfg.dot}`} />

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium">{task.name}</p>
              <p
                className={'text-sm text-muted-foreground mt-1 line-clamp-2'}
              >
                {task.description}
              </p>

              <div className="flex items-center gap-2 mt-3 flex-wrap">
                {parseAssignees(task.assignee).length > 0 ? (
                  <AssigneeBadges assignee={task.assignee} members={members} />
                ) : (
                  <span className="text-xs px-2 py-0.5 rounded-md border border-dashed text-muted-foreground/60 italic">
                    No assignee
                  </span>
                )}
                {task.priority ? (
                  <span className={`text-xs px-2 py-0.5 rounded-md border ${cfg.badge}`}>
                    {task.priority}
                  </span>
                ) : (
                  <span className="text-xs px-2 py-0.5 rounded-md border border-dashed text-muted-foreground/60 italic">
                    No priority
                  </span>
                )}
                {task.status ? (
                  <span className="text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground">
                    {task.status}
                  </span>
                ) : (
                  <span className="text-xs px-2 py-0.5 rounded-md border border-dashed text-muted-foreground/60 italic">
                    No status
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-gray-500 hover:text-gray-700"
                onClick={() => setEditing(true)}
                disabled={busy}
              >
                <Pen className="w-3.5 h-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-destructive"
                onClick={() => setShowDeleteDialog(true)}
                disabled={busy}
              >
                <Trash2 className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        )}
      </div>

      <Dialog
        open={showDeleteDialog}
        onOpenChange={(open) => { if (!open) setShowDeleteDialog(false); }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete task?</DialogTitle>
            <DialogDescription>
              You are about to delete <strong>{task.name}</strong>. This action{' '}
              <strong>cannot be undone</strong> — the task will be permanently removed.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
              disabled={busy}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={async () => {
                await onDelete();
                setShowDeleteDialog(false);
              }}
              disabled={busy}
            >
              Yes, delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AddStatusForm
        isOpen={showAddStatus}
        spaceId={spaceId}
        listId={listId}
        onClose={() => setShowAddStatus(false)}
        onSuccess={(updatedList: ClickUpListMetadata, addedStatus: string) => {
          if (updatedList.statuses) {
            setLocalStatuses(updatedList.statuses);
            setDraft((prev) => ({ ...prev, status: addedStatus }));
          }
          setShowAddStatus(false);
        }}
      />
    </>
  );
}