import type {
  ClickUpListMetadata,
  ClickUpTask,
  CreateTaskRequest,
  FolderWithListsMetadata,
  MemberDTO,
} from '@/api/api';
import { AddStatusForm } from './add-status-from';
import { Button } from './button';
import { Loader2, Plus } from 'lucide-react';
import { PriorityField } from './priority-field';
import { StatusField } from './status-field';
import { AssigneeSelect } from './assignee-select';
import { EditableField } from './editable-field';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { useNavigate } from 'react-router-dom';
import { useEffect, useMemo, useState, useCallback } from 'react';
import { defaultOnError } from '@/utils/error-handler';
import { clickupTaskManagementService } from '@/services/clickup-task-management-sevice';
import type { TaskDraft } from '@/types/clickup';
import { extractErrorCode, handleApiError, normalizeErrorMessage } from '@/services/api-error';
import { extractAssigneeListFromError } from '@/lib/extractAssigneeListFromError';
import { showSuccessToast } from '../global-toaster';

export type AssigneeDialogState =
  | { open: false }
  | { open: true; type: 'mails'; items: string[] };

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
  const [fieldErrors, setFieldErrors] = useState<{ name?: string; description?: string }>({});
  const [showAddStatus, setShowAddStatus] = useState(false);
  const [localStatuses, setLocalStatuses] = useState<string[]>(statuses);

  const [assigneeDialog, setAssigneeDialog] = useState<AssigneeDialogState>({ open: false });
  const [pendingReq, setPendingReq] = useState<CreateTaskRequest | null>(null);

  useEffect(() => setLocalStatuses(statuses), [statuses]);

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
    if (!draft.name.trim()) {
      errors.name = 'Task name cannot be empty.';
    }
    if (!draft.description.trim()) {
      errors.description = 'Description cannot be empty.';
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const canSubmit = draft.name.trim().length > 0 && draft.description.trim().length > 0 && !saving;

  const callCreate = useCallback(
    async (req: CreateTaskRequest) => {
      setSaving(true);

      try {
        const result = await clickupTaskManagementService.createTask(req);
        if (result) {
          onCreated(result);
          showSuccessToast('Click up task created successfully');
          setDraft(EMPTY_DRAFT);
          setFieldErrors({});
        }
      } catch (err: unknown) {
        const code = extractErrorCode(err);
        const message = normalizeErrorMessage(err);

        if (code === 'ASSIGNEE_EMAIL_NOT_IN_CLICKUP') {
          setPendingReq(req);
          setAssigneeDialog({ open: true, type: 'mails', items: extractAssigneeListFromError(message) });
        } else {
          onError(handleApiError(err), message);
        }
      } finally {
        setSaving(false);
      }
    },
    [onCreated, onError],
  );

  const handleCreate = async () => {
    if (!validate()) return;

    const req: CreateTaskRequest = {
      list_id: listId,
      space_id: spaceId,
      name: draft.name,
      description: draft.description,
      status: draft.status || null,
      priority: draft.priority || null,
      assignees: draft.assignees.length > 0 ? draft.assignees.join(',') : null,
      ignore_mails: false,
    };

    await callCreate(req);
  };

  const handleIgnoreMails = useCallback(async () => {
    setAssigneeDialog({ open: false });
    if (!pendingReq) return;
    await callCreate({ ...pendingReq, ignore_mails: true });
    setPendingReq(null);
  }, [pendingReq, callCreate]);

  const handleCancelIgnoreMails = useCallback(() => {
    setAssigneeDialog({ open: false });
    setPendingReq(null);
  }, []);

  return (
    <>
      <div className="border border-ring rounded-xl px-4 py-3.5 space-y-3 bg-card">
        <p className="text-xs font-medium text-muted-foreground">New task</p>

        <div className="space-y-1">
          <EditableField
            value={draft.name}
            onChange={(v) => set('name')(v)}
            placeholder="Task name"
            className={`font-medium ${fieldErrors.name ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15' : ''}`}
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
            className={fieldErrors.description ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15' : ''}
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
            disabled={!canSubmit}
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

      <Dialog
        open={assigneeDialog.open && assigneeDialog.type === 'mails'}
        onOpenChange={(open) => { if (!open) handleCancelIgnoreMails(); }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Some assignee emails were not found in ClickUp. Do you want to ignore them?
            </DialogTitle>
            <DialogDescription>
              The following emails could not be matched to any ClickUp workspace member and
              will be left unassigned. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          {assigneeDialog.open && assigneeDialog.type === 'mails' && (
            <ul className="mt-1 space-y-1">
              {assigneeDialog.items.map((mail) => (
                <li
                  key={mail}
                  className="text-sm px-3 py-1.5 rounded-md bg-muted text-foreground font-medium"
                >
                  {mail}
                </li>
              ))}
            </ul>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={handleCancelIgnoreMails}>
              No
            </Button>
            <Button onClick={handleIgnoreMails}>Yes</Button>
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
            set('status')(addedStatus);
          }
          setShowAddStatus(false);
        }}
      />
    </>
  );
}