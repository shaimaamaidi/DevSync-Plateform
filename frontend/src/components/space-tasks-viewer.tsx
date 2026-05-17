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
import { useQueryClient } from '@tanstack/react-query';
import { extractErrorCode, handleApiError, normalizeErrorMessage, withErrorHandling } from '@/services/api-error';
import type {
  ClickUpTask,
  ClickUpList,
  UpdateTaskRequest,
  FolderWithListsMetadata,
  ClickUpListMetadata,
} from '@/api/api';
import { clickupTaskManagementService } from '@/services/clickup-task-management-sevice';
import { useMembers } from '@/hooks/member-hooks/use-members';
import { ViewerSkeleton } from './ui/viewer-skeletion-card';
import { AddTaskForm } from './ui/add-task-form';
import { TaskCard } from './ui/task-card';
import { buildLocationWithTasksOptions } from '@/lib/location';
import { extractAssigneeListFromError } from '@/lib/extractAssigneeListFromError';
import { useSpaceTasks } from '@/hooks/clickup-space-hooks/clickup-space-tasks';
import { showSuccessToast } from './global-toaster';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { defaultOnError } from '@/utils/error-handler';
import { CreateListForm } from './ui/create-list-form'; 

export type AssigneeDialogState =
  | { open: false }
  | { open: true; type: 'mails'; items: string[] };

type PendingUpdate = {
  taskId: string;
  req: Omit<UpdateTaskRequest, 'task_id' | 'space_id'>;
};

export function SpaceTasksViewer() {
  const { spaceId } = useParams<{ spaceId: string }>();
  const [selectedListId, setSelectedListId] = useState<string>('');

  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  const { members, loading: membersLoading } = useMembers();
  const { folders, loading: dataLoading, error: dataError } = useSpaceTasks(spaceId ?? '');
  const [extraLists, setExtraLists] = useState<ClickUpListMetadata[]>([]);
  const [tasksByList, setTasksByList] = useState<Record<string, ClickUpTask[]>>({});

  const [showAddForm, setShowAddForm] = useState(false);
  const [showCreateListForm, setShowCreateListForm] = useState(false);
  const [busy, setBusy] = useState(false);

  const [assigneeDialog, setAssigneeDialog] = useState<AssigneeDialogState>({ open: false });
  const [pendingUpdate, setPendingUpdate] = useState<PendingUpdate | null>(null);

  const locationOptions = useMemo(() => {
    const base = buildLocationWithTasksOptions(folders);
    const extra = extraLists
      .filter((l) => !base.some((o) => o.listId === l.id))
      .map((l) => ({
        listId: l.id,
        label: l.name,
        list: { 
          id: l.id, 
          name: l.name, 
          statuses: l.statuses ?? [],
          priorities: l.priorities ?? [] 
        } as ClickUpList,
      }));
    return [...base, ...extra];
  }, [folders, extraLists]);

  const selectedOption = locationOptions.find((o) => o.listId === selectedListId);
  const selectedList: ClickUpList | null = selectedOption?.list ?? null;
  const statuses: string[] = selectedList?.statuses ?? [];
  const priorities: string[] = selectedList?.priorities ?? [];
  const currentTasks: ClickUpTask[] = tasksByList[selectedListId] ?? [];
  const emptyStructureForFields: FolderWithListsMetadata[] = [];
  
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


  const handleCreated = useCallback((task: ClickUpTask) => {
    setTasksByList((prev) => ({
      ...prev,
      [selectedListId]: [task, ...(prev[selectedListId] ?? [])],
    }));
    setShowAddForm(false);
  }, [selectedListId]);

  const handleListCreated = useCallback((list: ClickUpListMetadata) => {
    setExtraLists((prev) => [...prev, list]);  
    setTasksByList((prev) => ({ ...prev, [list.id]: [] }));  
    setSelectedListId(list.id);              
    setShowCreateListForm(false);
    queryClient.invalidateQueries({ queryKey: ['space-tasks', spaceId] });
  }, []);

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
              <h2 className="text-2xl font-bold text-foreground">Click Up Space Tasks</h2>
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
                  No location available.
                </p>
              ) : (
                <div className="flex items-center justify-between gap-3">
                  <div className="flex-1 max-w-sm">
                    <Select
                      value={selectedListId || 'none'}
                      onValueChange={(val) => setSelectedListId(val === 'none' ? '' : val)}
                      disabled={busy}
                    >
                      <SelectTrigger
                        className={`w-full max-w-sm bg-input border-border ${
                          !selectedListId || selectedListId === 'none'
                            ? 'text-muted-foreground'
                            : 'text-foreground'
                        }`}
                      >
                        { dataLoading ? (
                            <span className="text-muted-foreground">Loading…</span>
                          ) : (
                            <SelectValue placeholder="No click up location selected" />
                        )}                      
                      </SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        { dataLoading ? (
                          <div className="px-3 py-2 text-xs text-muted-foreground">Loading…</div>
                        ):
                          locationOptions.length === 0 ? (
                          <SelectItem value="none" className="text-muted-foreground" disabled>
                            No location available
                          </SelectItem>
                        ) : (
                          <>
                            <SelectItem value="none" className="text-muted-foreground" disabled>No location selected</SelectItem>
                            {locationOptions.map((opt) => (
                              <SelectItem key={opt.listId} value={opt.listId}>
                                {opt.label}
                              </SelectItem>
                            ))}
                          </>
                        )}
                      </SelectContent>
                    </Select>
                    <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                  </div>

                  <div className="ml-auto">
                    <Button
                      onClick={() => setShowCreateListForm(true)}
                      disabled={busy}
                      className="gap-2"
                    >
                      <Plus className="w-4 h-4" />
                      New click up location
                    </Button>
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

      <CreateListForm
        isOpen={showCreateListForm}
        onClose={() => setShowCreateListForm(false)}
        onSuccess={handleListCreated}
        spaceId={spaceId!}
      />
    </>
  );
}