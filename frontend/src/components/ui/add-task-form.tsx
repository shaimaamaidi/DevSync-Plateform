import type { ClickUpListMetadata, ClickUpTask, CreateTaskRequest, FolderWithListsMetadata, MemberDTO } from "@/api/api";
import { AddStatusForm } from "./add-status-from";
import { Button } from "./button";
import { AlertCircle, Loader2, Plus } from "lucide-react";
import { PriorityField } from "./priority-field";
import { StatusField } from "./status-field";
import { AssigneeSelect } from "./assignee-select";
import { EditableField } from "./editable-field";
import { useNavigate } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { defaultOnError } from "@/utils/error-handler";
import { withErrorHandling } from "@/services/api-error";
import { clickupTaskManagementService } from "@/services/clickup-task-management-sevice";
import type { TaskDraft } from "@/types/clickup";

const EMPTY_DRAFT: TaskDraft = {
  name: '',
  description: '',
  status: '',
  priority: '',
  assignees: [],
};

interface AddTaskFormProps {
  listId: string;
  spaceId: string;
  statuses: string[];
  priorities: string[];
  structureForFields: FolderWithListsMetadata[];
  structureLoading: boolean;
  members: MemberDTO[];
  membersLoading: boolean;
  onCreated: (task: ClickUpTask) => void;
  onCancel: () => void;
}

export function AddTaskForm({
  listId,
  spaceId,
  statuses,
  priorities,
  structureForFields,
  structureLoading,
  members,
  membersLoading,
  onCreated,
  onCancel,
}: AddTaskFormProps) {
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  const [draft, setDraft] = useState<TaskDraft>(EMPTY_DRAFT);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddStatus, setShowAddStatus] = useState(false);
  const [localStatuses, setLocalStatuses] = useState<string[]>(statuses);

  useEffect(() => setLocalStatuses(statuses), [statuses]);

  const set =
    <K extends keyof TaskDraft>(key: K) =>
    (value: TaskDraft[K]) =>
      setDraft((prev) => ({ ...prev, [key]: value }));

  const handleCreate = async () => {
    if (!draft.name.trim()) {
      setError('Task name is required.');
      return;
    }
    setSaving(true);
    setError(null);

    const req: CreateTaskRequest = {
      list_id: listId,
      space_id: spaceId,
      name: draft.name,
      description: draft.description,
      status: draft.status || null,
      priority: draft.priority || null,
      assignees: draft.assignees.length > 0 ? draft.assignees.join(',') : null,
    };
    console.log(req);
    const result = await withErrorHandling(
      () => clickupTaskManagementService.createTask(req),
      'Create ClickUp task',
      onError,
    );

    setSaving(false);

    if (result) {
      onCreated(result);
      setDraft(EMPTY_DRAFT);
    } else {
      setError('Failed to create task. Please try again.');
    }
  };

  return (
    <>
      <div className="border border-ring rounded-xl px-4 py-3.5 space-y-3 bg-card">
        <p className="text-xs font-medium text-muted-foreground">New task</p>

        {error && (
          <div className="flex items-center gap-2 text-xs text-destructive">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
            {error}
          </div>
        )}

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
          <Button variant="outline" size="sm" onClick={onCancel} disabled={saving}>
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleCreate}
            disabled={saving || !draft.name.trim()}
            className="gap-2"
          >
            {saving ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Plus className="w-3.5 h-3.5" />
            )}
            Add task
          </Button>
        </div>
      </div>

      <AddStatusForm
        isOpen={showAddStatus}
        spaceId={spaceId}
        listId={listId}
        onClose={() => setShowAddStatus(false)}
        onSuccess={(updatedList: ClickUpListMetadata, addedStatus: string) => {
          if (updatedList.statuses) {
            setLocalStatuses(updatedList.statuses);
            set('status')(addedStatus);
          }
          setShowAddStatus(false);
        }}
      />
    </>
  );
}
