import type { ClickUpListMetadata, ClickUpTask, FolderWithListsMetadata, MemberDTO, UpdateTaskRequest } from "@/api/api";
import { AddStatusForm } from "./add-status-from";
import { Loader2, Pen, Trash2 } from "lucide-react";
import { Button } from "./button";
import { PriorityField } from "./priority-field";
import { StatusField } from "./status-field";
import { AssigneeSelect } from "./assignee-select";
import { EditableField } from "./editable-field";
import { useEffect, useState } from "react";
import { priorityConfig, type TaskDraft } from "@/lib/tasks-utils";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "./dialog";

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
  const [expanded, setExpanded] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showAddStatus, setShowAddStatus] = useState(false);
  const [localStatuses, setLocalStatuses] = useState<string[]>(statuses);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const [draft, setDraft] = useState<TaskDraft>({
    name: task.name,
    description: task.description,
    status: task.status,
    priority: task.priority ?? '',
    assignees: parseAssignees(task.assignee),
  });

  useEffect(() => setLocalStatuses(statuses), [statuses]);

  useEffect(() => {
    setDraft({
      name: task.name,
      description: task.description,
      status: task.status,
      priority: task.priority ?? '',
      assignees: parseAssignees(task.assignee),
    });
  }, [task]);

  const set =
    <K extends keyof TaskDraft>(key: K) =>
    (value: TaskDraft[K]) =>
      setDraft((prev) => ({ ...prev, [key]: value }));

  const handleSave = async () => {
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

  const cfg = priorityConfig(task.priority ?? '');

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

            <EditableField
              value={draft.name}
              onChange={(v) => set('name')(v)}
              placeholder="Task name"
              className="font-medium"
            />

            <EditableField
              value={draft.description}
              onChange={(v) => set('description')(v)}
              type="textarea"
              placeholder="Description"
            />

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
                onClick={() => {
                  setDraft({
                    name: task.name,
                    description: task.description,
                    status: task.status,
                    priority: task.priority ?? '',
                    assignees: parseAssignees(task.assignee),
                  });
                  setEditing(false);
                }}
                disabled={saving || busy}
              >
                Cancel
              </Button>
              <Button size="sm" onClick={handleSave} disabled={saving || busy}>
                {saving && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
                Save
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-3">
            <div className={`w-2 h-2 mt-[7px] rounded-full flex-shrink-0 ${cfg.dot}`} />

            <div
              className="flex-1 min-w-0 cursor-pointer"
              onClick={() => setExpanded((p) => !p)}
            >
              <p className="text-sm font-medium">{task.name}</p>
              <p
                className={`text-sm text-muted-foreground mt-1 ${
                  expanded ? '' : 'line-clamp-2'
                }`}
              >
                {task.description}
              </p>

              <div className="flex items-center gap-2 mt-3 flex-wrap">
                {task.assignee && (
                  <span className="text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground">
                    👤 {task.assignee}
                  </span>
                )}
                {task.priority && (
                  <span className={`text-xs px-2 py-0.5 rounded-md border ${cfg.badge}`}>
                    {task.priority}
                  </span>
                )}
                {task.status && (
                  <span className="text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground">
                    {task.status}
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

      {/* Delete confirmation dialog */}
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