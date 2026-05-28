import { Button } from '@/components/ui/button';
import { ShieldCheck } from 'lucide-react';
import type { FolderWithListsMetadata } from '@/api/api';
import { GeneratedTaskCard } from './ui/generated-task-card';
import { TaskSkeletonCard } from './ui/tasks-skeleton-card';
import type { TaskGenerationDTO } from '@/types/clickup';

interface Props {
  tasks: TaskGenerationDTO[];
  isLoading: boolean;
  onUpdate: (index: number, updated: TaskGenerationDTO) => void;
  onDelete: (index: number) => void;
  onVerify: () => void;
  isVerifying: boolean;
  canVerify: boolean;
  structure: FolderWithListsMetadata[];
  structureLoading: boolean;
  spaceId: string;
  isVerificationFinished: boolean;
  disabled: boolean;
  showEstimation?: boolean;
}

export function GeneratedTaskList({
  tasks,
  isLoading,
  onUpdate,
  onDelete,
  onVerify,
  isVerifying,
  canVerify,
  structure,
  structureLoading,
  spaceId,
  isVerificationFinished,
  disabled,
  showEstimation = false,
}: Props) {
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
        <p className="text-xs text-muted-foreground">
          {!isLoading &&
            `${tasks.length} task${tasks.length !== 1 ? 's' : ''} generated${isVerificationFinished ? ' · drag any task into Step 3 to add it manually' : ''}`}
        </p>
        {isVerificationFinished && (
          <span className="text-xs text-muted-foreground/60">⇠ drag</span>
        )}
      </div>

      <div className="max-h-[480px] overflow-y-auto overflow-x-auto flex flex-col gap-2 pr-1 max-w-full">
        {isLoading
          ?  Array.from({ length: 3 }).map((_, i) => <TaskSkeletonCard key={i} />)
          : tasks.map((task, i) => (
              <GeneratedTaskCard
                key={`${task.task_name}-${i}`}
                task={task}
                onDelete={() => onDelete(i)}
                onUpdate={updated => onUpdate(i, updated)}
                structure={structure}
                structureLoading={structureLoading}
                spaceId={spaceId}
                isVerificationFinished={isVerificationFinished}
                disabled ={disabled}
                isVerifying={isVerifying}
                showEstimation={showEstimation}
              />
            ))}
      </div>

      {!isLoading && tasks.length === 0 &&(
        <div className="text-center py-8 text-sm text-muted-foreground border border-dashed rounded-xl">
          <p>No tasks could be extracted from this summary.</p>
        </div>
      )}

      {!isLoading && tasks.length > 0 && (
        <div className="flex flex-wrap items-center justify-end gap-2 pt-1">
          {!canVerify && (
            <p className="text-xs text-amber-600 text-right">
              All tasks need a location before verifying.
            </p>
          )}
          <Button
            onClick={onVerify}
            disabled={isVerifying || !canVerify || disabled}
            variant="outline"
            className="gap-2"
          >
            <ShieldCheck className="w-4 h-4" />
            {isVerifying ? 'Verifying…' : 'Verify tasks'}
          </Button>
        </div>
      )}
    </div>
  );
}