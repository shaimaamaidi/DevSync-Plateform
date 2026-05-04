import { Button } from '@/components/ui/button';
import { ShieldCheck } from 'lucide-react';
import type { GeneratedTask } from '@/api/api';
import { GeneratedTaskCard } from './ui/generated-task-card';
import { GeneratedTaskSkeletonCard } from './ui/generated-task-skeleton-card';


interface Props {
  tasks: GeneratedTask[];
  isLoading: boolean;
  onDelete: (index: number) => void;
  onVerify: () => void;
  isVerifying: boolean;
}

export function GeneratedTaskList({
  tasks,
  isLoading,
  onDelete,
  onVerify,
  isVerifying,
}: Props) {
  return (
    <div className="space-y-3">
      {/* header */}
      <div className="flex items-center justify-between mb-1">
        <p className="text-xs text-muted-foreground">
          {isLoading
            ? 'Generating…'
            : `${tasks.length} task${tasks.length !== 1 ? 's' : ''} · drag into Step 3`}
        </p>
        <span className="text-xs text-muted-foreground/60">⇠ drag</span>
      </div>

      {/* list */}
      <div className="flex flex-col gap-2">
        {isLoading
          ? Array.from({ length: 3 }).map((_, i) => (
              <GeneratedTaskSkeletonCard key={i} />
            ))
          : tasks.map((task, i) => (
              <GeneratedTaskCard
                key={`${task.task_name}-${i}`}
                task={task}
                onDelete={() => onDelete(i)}
              />
            ))}
      </div>

      {/* footer */}
      {!isLoading && tasks.length > 0 && (
        <div className="flex justify-end pt-1">
          <Button
            onClick={onVerify}
            disabled={isVerifying}
            variant="outline"
            className="gap-2"
          >
            <ShieldCheck className="w-4 h-4" />
            {isVerifying ? 'Verifying…' : 'Verify tasks →'}
          </Button>
        </div>
      )}
    </div>
  );
}