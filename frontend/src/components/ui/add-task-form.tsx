import type {
  ClickUpListMetadata,
  ClickUpTask,
  CreateTaskRequest,
  FolderWithListsMetadata,
  MemberDTO,
} from '@/api/api';
import { AddStatusForm } from './add-status-from';
import { Button } from './button';
import { AlertCircle, Loader2, Plus } from 'lucide-react';
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
import { useEffect, useState, useCallback } from 'react';
import { clickupTaskManagementService } from '@/services/clickup-task-management-sevice';
import type { TaskDraft } from '@/types/clickup';
import { showSuccessToast } from '../global-toaster';
import { defaultOnError } from '@/services/api-error';
import { resolveErrorAction, extractStatusCode, normalizeErrorMessage, extractErrorCode, extractAssigneeListFromError } from '@/utils/error-handler';
import { createPortal } from 'react-dom';
import type { AssigneeDialogStateForConsultation } from '@/types/assignee-dialog';

const EMPTY_DRAFT: TaskDraft = {
  name: '',
  description: '',
  status: '',
  priority: '',
  assignees: [],
};

interface AddTaskFormProps {
  isOpen: boolean;
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
  isOpen,
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
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const [draft, setDraft] = useState<TaskDraft>(EMPTY_DRAFT);
  const [saving, setSaving] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ name?: string; description?: string }>({});
  const [showAddStatus, setShowAddStatus] = useState(false);
  const [localStatuses, setLocalStatuses] = useState<string[]>(statuses);

  const [assigneeDialog, setAssigneeDialog] = useState<AssigneeDialogStateForConsultation>({ open: false });
  const [pendingReq, setPendingReq] = useState<CreateTaskRequest | null>(null);
  const canSubmit = !saving;

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
    setFieldErrors({});
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

  const callCreate = useCallback(
    async (req: CreateTaskRequest) => {
      setSaving(true);
      try {
        const result = await clickupTaskManagementService.createTask(req);
        if (result) {
          onCreated(result);
          showSuccessToast('Click up task created successfully');
          onCancel();
          setDraft(EMPTY_DRAFT);
          setFieldErrors({});
        }
      } catch (err: unknown) {
        const code = extractErrorCode(err);
        const status = extractStatusCode(err);
        const message = normalizeErrorMessage(err);

        if (code === 'ASSIGNEE_EMAIL_NOT_IN_CLICKUP') {
          setPendingReq(req);
          setAssigneeDialog({ open: true, type: 'mails', items: extractAssigneeListFromError(message) });
        } else {
          const action = resolveErrorAction(err);
          await onError()(action, message, { code, status: status ?? undefined });
        }
      } finally {
        setSaving(false);
      }
    },
    [onCreated, onError],
  );

  const handleCreate = async () => {
    if (!validate()) 
      return;

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

  if (!isOpen)
    return null;

  return (
    <>
      <div className="border border-ring rounded-xl bg-card flex flex-col max-h-[70vh] sm:max-h-[70vh]">

        <div className="px-3 sm:px-4 pt-3 sm:pt-3.5 pb-2 shrink-0">
          <p className="text-xs font-medium text-muted-foreground">New task</p>
        </div>

        <div className="space-y-3 px-3 sm:px-4 py-2 overflow-y-auto flex-1">
          <div className="space-y-1">
            <EditableField
              value={draft.name}
              onChange={(v) => set('name')(v)}
              placeholder="Task name"
              className={`font-medium ${fieldErrors.name ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15' : ''}`}
            />
            {fieldErrors.name && (
              <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {fieldErrors.name}
              </div>
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
              <div className="text-destructive text-xs mt-1 px-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {fieldErrors.description}
              </div>
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
        </div>

        <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 px-3 sm:px-4 pb-3 sm:pb-3.5 pt-3 border-t border-border shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={onCancel}
            disabled={saving}
            className="w-full sm:w-auto"
          >
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleCreate}
            disabled={!canSubmit}
            className="gap-2 w-full sm:w-auto"
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
        <DialogContent
          className="w-[calc(100%-2rem)] sm:w-full max-w-lg mx-auto"
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg leading-snug">
              Some assignee emails were not found in ClickUp. Do you want to ignore them?
            </DialogTitle>
            <DialogDescription className="text-sm">
              The following emails could not be matched to any ClickUp workspace member and
              will be left unassigned. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          {assigneeDialog.open && assigneeDialog.type === 'mails' && (
            <ul className="mt-1 space-y-1 max-h-40 overflow-y-auto">
              {assigneeDialog.items.map((mail) => (
                <li
                  key={mail}
                  className="text-sm px-3 py-1.5 rounded-md bg-muted text-foreground font-medium break-all"
                >
                  {mail}
                </li>
              ))}
            </ul>
          )}

          <DialogFooter className="flex-col-reverse sm:flex-row gap-2">
            <Button variant="outline" onClick={handleCancelIgnoreMails} className="w-full sm:w-auto">
              No
            </Button>
            <Button onClick={handleIgnoreMails} className="w-full sm:w-auto">
              Yes
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
              set('status')(addedStatus);
            }
            setShowAddStatus(false);
          }}
        />,
        document.body
      )}
    </>
  );
}