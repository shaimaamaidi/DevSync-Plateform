import type { 
  ClickUpListMetadata, 
  ClickUpTaskWithEstimation, 
  FolderWithListsMetadata, 
  MemberDTO, 
  UpdateTaskRequest 
} from "@/api/api";
import { useEffect, useState } from "react";
import type { TaskDraft } from "@/types/clickup";
import { priorityConfig } from "@/lib/priority";
import { createPortal } from "react-dom";
import { EditableField } from "../task-detail-controls/editable-field";
import { AssigneeSelect } from "../task-detail-controls/assignee-select";
import { StatusField } from "../task-detail-controls/status-field";
import { PriorityField } from "../task-detail-controls/priority-field";
import { Button } from "../shared-primitives/button";
import { Clock, Loader2, Pen, Trash2 } from "lucide-react";
import { AssigneeBadges } from "../task-detail-controls/assignee-badge";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from "../shared-primitives/dialog";
import { AddStatusForm } from "../clickup-creation-forms/add-status-from";
import { useCurrentUser } from "@/hooks/current-user-hooks/use-current-user";

interface TaskCardProps {
  task: ClickUpTaskWithEstimation;
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

function parseAssignees(raw: string | null | undefined): string[] {
  return raw ? raw.split(',').map((s) => s.trim()).filter(Boolean) : [];
}

function buildInitialDraft(task: ClickUpTaskWithEstimation): TaskDraft {
  return {
    name: task.name,
    description: task.description ?? "",
    status: task.status ?? "",
    priority: task.priority ?? "",
    assignees: parseAssignees(task.assignee),
    estimation: task.estimation ?? null,
  };
}

function isDraftDirty(draft: TaskDraft, task: ClickUpTaskWithEstimation): boolean {
  return (
    draft.name !== task.name ||
    draft.description !== task.description ||
    draft.status !== task.status ||
    draft.priority !== (task.priority ?? '') ||
    draft.assignees.join(',') !== parseAssignees(task.assignee).join(',') ||
    (draft.estimation ?? null) !== (task.estimation ?? null)
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
  const { user: currentUser, loading } = useCurrentUser();
  const isAdmin = !loading && currentUser?.role === 'admin';
  
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showAddStatus, setShowAddStatus] = useState(false);
  const [localStatuses, setLocalStatuses] = useState<string[]>(statuses);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ name?: string; description?: string; form?: string }>({});

  const [draft, setDraft] = useState<TaskDraft>(() => buildInitialDraft(task));
  const isDirty = isDraftDirty(draft, task);
  const canSave = !saving && !busy;

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
    setFieldErrors({});
    const errors: { name?: string; description?: string; form?: string } = {};

    if (editing && isDirty){
      errors.form = 'No changes to update';
    }
    if (!draft.name?.trim()) {
      errors.name = 'Task name cannot be empty.';
    }
    if (!draft.description?.trim()) {
      errors.description = 'Description cannot be empty.';
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) 
      return;

    setSaving(true);

    await onSave({
      name: draft.name,
      description: draft.description,
      status: draft.status,
      priority: draft.priority || null,
      assignees: draft.assignees.length > 0 ? draft.assignees.join(',') : null,
      old_assignees: task.assignee ?? null,
      estimation: draft.estimation ?? null,
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
        className={`border rounded-xl px-3 sm:px-4 py-3 sm:py-3.5 transition-colors ${
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

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div className="col-span-1 sm:col-span-2">
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

              <div>
                <p className="text-xs text-muted-foreground mb-1">Estimation (hours)</p>
                <EditableField
                  value={draft.estimation != null ? String(draft.estimation) : ''}
                  onChange={(v) => {
                    const parsed = parseFloat(v);
                    set('estimation')(!v.trim() || isNaN(parsed) ? null : parsed);
                  }}
                  placeholder="Optional (e.g. 2.5)"
                />
              </div>
            </div>

            <div className="flex flex-col-reverse sm:flex-row sm:justify-between gap-2 pt-1">
              {fieldErrors.form ? (
                <div className="text-destructive text-sm self-center">{fieldErrors.form}</div>
              ) : <div />}
              <div className="flex flex-col-reverse sm:flex-row gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCancel}
                  disabled={saving || busy}
                  className="w-full sm:w-auto"
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSave}
                  disabled={!canSave}
                  className="w-full sm:w-auto"
                >
                  {saving && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
                  Save
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-2 sm:gap-3">
            <div className={`w-2 h-2 mt-[7px] rounded-full flex-shrink-0 ${cfg.dot}`} />

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium break-words">{task.name}</p>
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2 break-words">
                {task.description}
              </p>

              <div className="flex items-center gap-2 mt-3 flex-wrap">
                {parseAssignees(task.assignee).length > 0 ? (
                  <AssigneeBadges assignee={task.assignee} members={members} />
                ) : (
                  <span className="text-xs px-2 py-0.5 rounded-md border border-dashed text-muted-foreground/60 italic shrink-0">
                    No assignee
                  </span>
                )}
                {task.priority ? (
                  <span className={`text-xs px-2 py-0.5 rounded-md border shrink-0 ${cfg.badge}`}>
                    {task.priority}
                  </span>
                ) : (
                  <span className="text-xs px-2 py-0.5 rounded-md border border-dashed text-muted-foreground/60 italic shrink-0">
                    No priority
                  </span>
                )}
                {task.status ? (
                  <span className="text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground shrink-0">
                    {task.status}
                  </span>
                ) : (
                  <span className="text-xs px-2 py-0.5 rounded-md border border-dashed text-muted-foreground/60 italic shrink-0">
                    No status
                  </span>
                )}
                {task.estimation != null ? (
                  <span className="text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground shrink-0 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {task.estimation}h
                  </span>
                ) : null}
              </div>
            </div>

            <div className="flex items-center gap-1 flex-shrink-0">
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-gray-500 hover:text-gray-700"
                onClick={() => setEditing(true)}
                disabled={busy}
              >
                <Pen className="w-3.5 h-3.5" />
              </Button>
              {isAdmin && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 w-7 p-0 text-destructive"
                  onClick={() => setShowDeleteDialog(true)}
                  disabled={busy}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </Button>
              )}
            </div>
          </div>
        )}
      </div>

      <Dialog
        open={showDeleteDialog}
        onOpenChange={(open) => { if (!open) setShowDeleteDialog(false); }}
      >
        <DialogContent
          className="w-[calc(100%-2rem)] sm:w-full max-w-lg mx-auto"
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg">Delete task?</DialogTitle>
            <DialogDescription className="text-sm">
              You are about to delete <strong>{task.name}</strong>. This action{' '}
              <strong>cannot be undone</strong> — the task will be permanently removed.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col-reverse sm:flex-row gap-2">
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
              disabled={busy}
              className="w-full sm:w-auto"
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
              className="w-full sm:w-auto"
            >
              Yes, delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {showAddStatus && createPortal(
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
        />,
        document.body
      )}
    </>
  );
}