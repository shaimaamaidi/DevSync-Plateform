import { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Plus, Save, Check } from 'lucide-react';

import type { GeneratedTask, VerifiedTask } from '@/api/api';
import { AddTaskForm } from './ui/add-task-form';
import { VerifiedTaskSkeletonCard } from './ui/verified-task-skeleton-card';
import { VerifiedTaskCard } from './ui/verified-task-card';


export const PRIORITY_CONFIG: Record<
  string,
  { badge: string; dot: string }
> = {
  urgent: { badge: 'bg-red-50 text-red-700 border-red-100', dot: 'bg-red-500' },
  high: { badge: 'bg-amber-50 text-amber-700 border-amber-100', dot: 'bg-amber-500' },
  medium: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  normal: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  low: { badge: 'bg-muted text-muted-foreground border-border', dot: 'bg-muted-foreground' },
};

export function priorityConfig(p: string) {
  return PRIORITY_CONFIG[p?.toLowerCase()] ?? PRIORITY_CONFIG.normal;
}


interface Props {
  tasks: VerifiedTask[];
  isLoading: boolean;
  onChange: (tasks: VerifiedTask[]) => void;
  onDrop: (task: GeneratedTask) => void;
  onSave: () => void;
  isSaving: boolean;
  savedOk: boolean;
}

export function VerifiedTaskList({
  tasks,
  isLoading,
  onChange,
  onDrop,
  onSave,
  isSaving,
  savedOk,
}: Props) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const dropRef = useRef<HTMLDivElement>(null);


  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const raw = e.dataTransfer.getData('application/x-generated-task');
    if (!raw) return;

    try {
      onDrop(JSON.parse(raw));
    } catch {}
  };

  const handleDelete = (idx: number) =>
    onChange(tasks.filter((_, i) => i !== idx));

  const handleUpdate = (idx: number, updated: VerifiedTask) =>
    onChange(tasks.map((t, i) => (i === idx ? updated : t)));

  const handleAdd = (task: VerifiedTask) => {
    onChange([...tasks, task]);
    setShowAddForm(false);
  };


  return (
    <div
      ref={dropRef}
      onDragOver={e => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      className={`space-y-3 rounded-xl transition ${
        isDragOver ? 'ring-2 ring-primary/40 bg-primary/5 p-2' : ''
      }`}
    >
      {/* header */}
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          {isLoading
            ? 'Verifying…'
            : `${tasks.length} task${tasks.length !== 1 ? 's' : ''} · drop or add`}
        </p>

        {!isLoading && (
          <Button
            variant="outline"
            size="sm"
            className="gap-1 h-7 text-xs"
            onClick={() => setShowAddForm(p => !p)}
          >
            <Plus className="w-3 h-3" />
            Add task
          </Button>
        )}
      </div>

      {/* add form */}
      {showAddForm && (
        <AddTaskForm
          onAdd={handleAdd}
          onCancel={() => setShowAddForm(false)}
        />
      )}

      {/* list */}
      <div className="flex flex-col gap-2">
        {isLoading
          ? Array.from({ length: 3 }).map((_, i) => (
              <VerifiedTaskSkeletonCard key={i} />
            ))
          : tasks.map((task, i) => (
              <VerifiedTaskCard
                key={`${task.task_name}-${i}`}
                task={task}
                onDelete={() => handleDelete(i)}
                onUpdate={updated => handleUpdate(i, updated)}
                priorityConfig={priorityConfig}  
              />
            ))}
      </div>

      {/* empty state */}
      {!isLoading && tasks.length === 0 && !showAddForm && (
        <div className="text-center py-8 text-sm text-muted-foreground border border-dashed rounded-xl">
          No tasks yet — drag or add manually
        </div>
      )}

      {/* save section */}
      {!isLoading && tasks.length > 0 && (
        <div className="flex justify-end gap-3 pt-2">
          {savedOk && (
            <span className="flex items-center gap-1 text-green-600 text-sm">
              <Check className="w-4 h-4" />
              Saved
            </span>
          )}

          <Button
            onClick={onSave}
            disabled={isSaving}
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