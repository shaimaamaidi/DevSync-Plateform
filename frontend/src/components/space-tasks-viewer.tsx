import { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Plus,
  AlertCircle,
  ChevronDown,
  ArrowLeft,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { useNavigate, useParams } from 'react-router-dom';
import { extractErrorCode, handleApiError, normalizeErrorMessage, withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import type {
  ClickUpTask,
  ClickUpList,
  UpdateTaskRequest,
  FolderWithListsMetadata,
} from '@/api/api';
import { clickupTaskManagementService } from '@/services/clickup-task-management-sevice';
import { useMembers } from '@/hooks/member-hooks/use-members';
import { ViewerSkeleton } from './ui/viewer-skeletion-card';
import { AddTaskForm } from './ui/add-task-form';
import { TaskCard } from './ui/task-card';
import { buildLocationWithTasksOptions } from '@/lib/location';
import { extractAssigneeListFromError } from '@/lib/extractAssigneeListFromError';
import { useSpaceTasks } from '@/hooks/clickup-space-hooks/clickup-space-tasks';
import type { AssigneeDialogState } from '@/types/clickup';
import { showSuccessToast } from './global-toaster';

type PendingUpdate = {
  taskId: string;
  req: Omit<UpdateTaskRequest, 'task_id' | 'space_id'>;
};

export function SpaceTasksViewer() {
  const { spaceId } = useParams<{ spaceId: string }>();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  const { members, loading: membersLoading } = useMembers();

  const { folders, loading: dataLoading, error: dataError } = useSpaceTasks(spaceId ?? '');

  const locationOptions = useMemo(
    () => buildLocationWithTasksOptions(folders),
    [folders],
  );

  const [selectedListId, setSelectedListId] = useState<string>('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [busy, setBusy] = useState(false);

  const [tasksByList, setTasksByList] = useState<Record<string, ClickUpTask[]>>({});

  const [assigneeDialog, setAssigneeDialog] = useState<AssigneeDialogState>({ open: false });
  const [pendingUpdate, setPendingUpdate] = useState<PendingUpdate | null>(null);

  useEffect(() => {
    if (folders.length === 0) 
      return;

    const map: Record<string, ClickUpTask[]> = {};
    for (const folder of folders) {
      for (const list of folder.lists ?? []) {
        map[list.id] = list.tasks ?? [];
      }
    }
    setTasksByList(map);
  }, [folders]);

  useEffect(() => {
    setShowAddForm(false);
  }, [selectedListId]);

  const selectedOption = locationOptions.find((o) => o.listId === selectedListId);
  const selectedList: ClickUpList | null = selectedOption?.list ?? null;
  const statuses: string[] = selectedList?.statuses ?? [];
  const priorities: string[] = selectedList?.priorities ?? [];
  const currentTasks: ClickUpTask[] = tasksByList[selectedListId] ?? [];
  const emptyStructureForFields: FolderWithListsMetadata[] = [];

  const handleCreated = useCallback((task: ClickUpTask) => {
    setTasksByList((prev) => ({
      ...prev,
      [selectedListId]: [task, ...(prev[selectedListId] ?? [])],
    }));
    setShowAddForm(false);
  }, [selectedListId]);


  const handleDelete = async (taskId: string) => {
    setBusy(true);
    const result = await withErrorHandling(
      () => clickupTaskManagementService.deleteTask(taskId),
      'Delete click up task',
      onError,
    );
    if (result) {
      setTasksByList((prev) => ({
        ...prev,
        [selectedListId]: (prev[selectedListId] ?? []).filter((t) => t.id !== taskId),
      }));
      showSuccessToast('Click up task deleted successfully');
    }
    setBusy(false);
  };

  const callUpdate = useCallback(
    async (
      taskId: string,
      req: Omit<UpdateTaskRequest, 'task_id' | 'space_id'>,
      ignoreMails = false,
    ) => {
      setBusy(true);
      try {
        const updated = await clickupTaskManagementService.updateTask(spaceId!, {
          ...req,
          task_id: taskId,
          ignore_mails: ignoreMails,
        });
        if (updated) {
          setTasksByList((prev) => ({
            ...prev,
            [selectedListId]: (prev[selectedListId] ?? []).map((t) =>
              t.id === taskId ? updated : t,
            ),
          }));
          showSuccessToast('Click up task updated successfully');
        }
      } catch (err: unknown) {
        const code = extractErrorCode(err);
        const message = normalizeErrorMessage(err);

        if (code === 'ASSIGNEE_EMAIL_NOT_IN_CLICKUP') {
          setPendingUpdate({ taskId, req });
          setAssigneeDialog({ open: true, type: 'mails', items: extractAssigneeListFromError(message) });
        } else {
          onError(handleApiError(err), message);
        }
      } finally {
        setBusy(false);
      }
    },
    [spaceId, selectedListId, onError],
  );

  const handleUpdate = useCallback(
    (taskId: string, req: Omit<UpdateTaskRequest, 'task_id' | 'space_id'>) =>
      callUpdate(taskId, req, false),
    [callUpdate],
  );

  const handleIgnoreMails = useCallback(async () => {
    setAssigneeDialog({ open: false });
    if (!pendingUpdate) return;
    await callUpdate(pendingUpdate.taskId, pendingUpdate.req, true);
    setPendingUpdate(null);
  }, [pendingUpdate, callUpdate]);

  const handleCancelIgnoreMails = useCallback(() => {
    setAssigneeDialog({ open: false });
    setPendingUpdate(null);
  }, []);

  return (
    <>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/spaces')}
              className="h-8 w-8"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div>
              <h2 className="text-2xl font-bold text-foreground">Space Tasks</h2>
              <p className="text-xs text-muted-foreground font-mono mt-0.5">{spaceId}</p>
            </div>
          </div>

          {!dataLoading && !dataError && selectedListId && (
            <Button onClick={() => setShowAddForm((p) => !p)} disabled={busy} className="gap-2">
              <Plus className="w-4 h-4" />
              Add task
            </Button>
          )}
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          {dataLoading && <ViewerSkeleton />}

          {!dataLoading && dataError && (
            <div className="flex items-center gap-2 text-sm text-destructive py-4">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {dataError}
            </div>
          )}

          {!dataLoading && !dataError && (
            <>
              {locationOptions.length === 0 ? (
                <p className="text-sm text-muted-foreground italic text-center py-4">
                  No lists found in this space.
                </p>
              ) : (
                <div className="flex items-center gap-3">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide whitespace-nowrap">
                    Location
                  </span>
                  <div className="relative flex-1 max-w-sm">
                    <select
                      value={selectedListId}
                      onChange={(e) => setSelectedListId(e.target.value)}
                      className="w-full appearance-none rounded-md border border-border bg-background px-3 py-2 pr-8 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                    >
                      <option value="" disabled>Select a location…</option>
                      {locationOptions.map((opt) => (
                        <option key={opt.listId} value={opt.listId}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                  </div>
                </div>
              )}

              {!selectedListId ? (
                <div className="text-center py-10 text-sm text-muted-foreground border border-dashed rounded-xl">
                  Select a location first
                </div>
              ) : (
                <div className="space-y-3">
                  {showAddForm && (
                    <AddTaskForm
                      listId={selectedListId}
                      spaceId={spaceId!}
                      statuses={statuses}
                      priorities={priorities}
                      structureForFields={emptyStructureForFields}
                      structureLoading={false}
                      members={members}
                      membersLoading={membersLoading}
                      onCreated={handleCreated}
                      onCancel={() => setShowAddForm(false)}
                    />
                  )}

                  {currentTasks.length === 0 && !showAddForm ? (
                    <div className="text-center py-8 text-sm text-muted-foreground border border-dashed rounded-xl">
                      No tasks yet — add manually
                    </div>
                  ) : (
                    currentTasks.map((task) =>
                      task.id ? (
                        <TaskCard
                          key={task.id}
                          task={task}
                          statuses={statuses}
                          priorities={priorities}
                          structureForFields={emptyStructureForFields}
                          structureLoading={false}
                          listId={selectedListId}
                          spaceId={spaceId!}
                          members={members}
                          membersLoading={membersLoading}
                          busy={busy}
                          onDelete={() => task.id && handleDelete(task.id)}
                          onSave={(req) =>
                            task.id ? handleUpdate(task.id, req) : Promise.resolve()
                          }
                        />
                      ) : null,
                    )
                  )}

                  {!dataLoading && selectedListId && (
                    <p className="text-xs text-muted-foreground pt-2">
                      {currentTasks.length} task{currentTasks.length !== 1 ? 's' : ''}
                    </p>
                  )}
                </div>
              )}
            </>
          )}
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
            <Button variant="outline" onClick={handleCancelIgnoreMails}>No</Button>
            <Button onClick={handleIgnoreMails}>Yes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}