import { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Plus, Save, Check } from 'lucide-react';
import type { 
  GeneratedTask, 
  VerifiedTask, 
  FolderWithListsMetadata 
} from '@/api/api';
import { TaskSkeletonCard } from './ui/tasks-skeleton-card';
import { AddVerifiedTaskForm } from './ui/add-verified-task-form';
import { VerifiedTaskCard } from './ui/verified-task-card';
import { priorityConfig } from '@/lib/tasks-utils';


interface Props {
  tasks: VerifiedTask[];
  isLoading: boolean;
  onChange: (tasks: VerifiedTask[]) => void;
  onDrop: (task: GeneratedTask) => void;
  onSave: () => void;
  isSaving: boolean;
  savedOk: boolean;
  canSave: boolean;
  spaceId: string;
  structure: FolderWithListsMetadata[];
  structureLoading: boolean;
  isStructureEmpty: boolean;
  disabled: boolean;
}

export function VerifiedTaskList({
  tasks,
  isLoading,
  onChange,
  onDrop,
  onSave,
  isSaving,
  savedOk,
  canSave,
  spaceId,
  structure,
  structureLoading,
  isStructureEmpty,
  disabled,
}: Props) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const dropRef = useRef<HTMLDivElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const raw = e.dataTransfer.getData('application/x-generated-task');
    if (!raw) return;
    try { onDrop(JSON.parse(raw)); } catch {}
  };

  const handleDelete = (idx: number) =>
    onChange(tasks.filter((_, i) => i !== idx));

  const handleUpdate = (idx: number, updated: VerifiedTask) =>
    onChange(tasks.map((t, i) => (i === idx ? updated : t)));

  const handleAdd = (task: VerifiedTask) => {
    if (!task.task_priority)
      task.task_priority = 'normal';
    if(!task.task_status)
      task.task_status = 'todo';
    onChange([...tasks, task]);
    setShowAddForm(false);
  };

  return (
    <div
      ref={dropRef}
      onDragOver={e => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      className={`space-y-3 rounded-xl transition ${
        isDragOver ? 'ring-2 ring-primary/40 bg-primary/5 p-2' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        {!isStructureEmpty && (
          <p className="text-xs text-muted-foreground">
            {!isLoading &&
              `${tasks.length} task${tasks.length !== 1 ? 's' : ''} · drop or add`}
          </p>
        )}

        {isStructureEmpty && (
          <p className="text-xs text-muted-foreground">
            {!isLoading &&
            `${tasks.length} task${tasks.length !== 1 ? 's' : ''} gererated from the summary`}
          </p>
        )}

        {!isLoading && (
          <Button 
            onClick={() => setShowAddForm(p => !p)}
            disabled={disabled}
            className="gap-2"
          >
            <Plus className="w-4 h-4" />
            Add task
          </Button>
        )}
      </div>

      {showAddForm && (
        <AddVerifiedTaskForm
          onAdd={handleAdd}
          onCancel={() => setShowAddForm(false)}
          spaceId={spaceId}
        />
      )}

      <div className="flex flex-col gap-2">
        {isLoading
          ? Array.from({ length: 3 }).map((_, i) => <TaskSkeletonCard key={i} />)
          : tasks.map((task, i) => (
              <VerifiedTaskCard
                key={`${task.task_name}-${i}`}
                task={task}
                onDelete={() => handleDelete(i)}
                onUpdate={updated => handleUpdate(i, updated)}
                priorityConfig={priorityConfig}
                structure={structure}
                structureLoading={structureLoading}
                spaceId={spaceId}
                disabled={disabled}
              />
            ))}
      </div>

      {!isLoading && tasks.length === 0 && !showAddForm && !isStructureEmpty && (
        <div className="text-center py-8 text-sm text-muted-foreground border border-dashed rounded-xl">
          No tasks yet — drag or add manually
        </div>
      )}

      {!isLoading && tasks.length === 0 && !showAddForm && isStructureEmpty && (
        <div className="text-center py-8 text-sm text-muted-foreground border border-dashed rounded-xl">
          No tasks yet — add manually
        </div>
      )}

      {!isLoading && tasks.length > 0 && (
        <div className="relative  flex justify-end items-center gap-3 pt-2">
          {!canSave && (
            <p className="text-xs text-amber-600">
              All tasks need a location before saving.
            </p>
          )}
          {savedOk && (
            <span className="flex items-center gap-1 text-green-600 text-sm">
              <Check className="w-4 h-4" />
              Saved
            </span>
          )}
          <Button
            onClick={onSave}
            disabled={isSaving || !canSave || disabled}
            className="gap-2 bg-[#0F6E56] hover:bg-[#0a5442] text-white"
          >
            <Save className="w-4 h-4" />
            {isSaving ? 'Saving…' : 'Save'}
          </Button>
        </div>
      )}
    </div>
  );
}