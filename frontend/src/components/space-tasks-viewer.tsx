import { useState, useEffect, useMemo } from 'react';
import {
  Plus,
  AlertCircle,
  ChevronDown,
  ArrowLeft,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNavigate, useParams } from 'react-router-dom';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import type {
  ClickUpTask,
  ClickUpList,
  FolderWithLists,
  UpdateTaskRequest,
  FolderWithListsMetadata,
} from '@/api/api';
import { clickupTaskManagementService } from '@/services/clickup-task-management-sevice';
import { useMembers } from '@/hooks/member-hooks/use-members';
import { clickupSpaceTaskReaderService } from '@/services/clickup-space-task-reader';
import { ViewerSkeleton } from './ui/viewer-skeletion-card';
import { AddTaskForm } from './ui/add-task-form';
import { TaskCard } from './ui/task-card';
import { buildLocationWithTasksOptions } from '@/lib/location';

export function SpaceTasksViewer() {
  const { spaceId } = useParams<{ spaceId: string }>();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  const { members, loading: membersLoading } = useMembers();

  const [folders, setFolders] = useState<FolderWithLists[]>([]);
  const [dataLoading, setDataLoading] = useState(true);
  const [dataError, setDataError] = useState<string | null>(null);

  useEffect(() => {
    if (!spaceId) return;
    let cancelled = false;
    setDataLoading(true);
    setDataError(null);

    (async () => {
      const result = await withErrorHandling(
        () => clickupSpaceTaskReaderService.getTasksBySpace(spaceId),
        'Load space tasks',
        onError,
      );
      if (cancelled) return;
      setDataLoading(false);
      if (result) {
        setFolders(result);
      } else {
        setDataError('Unable to load tasks for this space.');
      }
    })();

    return () => { cancelled = true; };
  }, [spaceId]);

  const locationOptions = useMemo(
    () => buildLocationWithTasksOptions(folders),
    [folders],
  );

  const [selectedListId, setSelectedListId] = useState<string>('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [tasksByList, setTasksByList] = useState<Record<string, ClickUpTask[]>>({});

  useEffect(() => {
    if (folders.length === 0) return;
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

  const handleDelete = async (taskId: string) => {
    setBusy(true);
    const ok = await withErrorHandling(
      () => clickupTaskManagementService.deleteTask(taskId),
      'Delete ClickUp task',
      onError,
    );
    if (ok) {
      setTasksByList((prev) => ({
        ...prev,
        [selectedListId]: (prev[selectedListId] ?? []).filter((t) => t.id !== taskId),
      }));
    }
    setBusy(false);
  };

  const handleUpdate = async (
    taskId: string,
    req: Omit<UpdateTaskRequest, 'task_id' | 'space_id'>,
  ) => {
    setBusy(true);
    const updated = await withErrorHandling(
      () => clickupTaskManagementService.updateTask(spaceId!, { ...req, task_id: taskId }),
      'Update ClickUp task',
      onError,
    );
    if (updated) {
      setTasksByList((prev) => ({
        ...prev,
        [selectedListId]: (prev[selectedListId] ?? []).map((t) =>
          t.id === taskId ? updated : t,
        ),
      }));
    }
    setBusy(false);
  };

  const handleCreated = (task: ClickUpTask) => {
    setTasksByList((prev) => ({
      ...prev,
      [selectedListId]: [task, ...(prev[selectedListId] ?? [])],
    }));
    setShowAddForm(false);
  };

  return (
    <div className="space-y-4">
      {/* Header avec bouton retour */}
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

      {/* Body */}
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
  );
}