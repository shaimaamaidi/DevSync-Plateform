import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Trash2, GripVertical, Plus } from 'lucide-react';
import { Button } from '@/components/ui/shared-primitives/button';
import type { FolderWithListsMetadata } from '@/api/api';
import { AssigneeAvatars } from '../task-detail-controls/assignees-avatar';
import { CreateListForm } from '../clickup-creation-forms/create-list-form';
import { buildLocationWithMetadataOptions } from '@/lib/location';
import { priorityConfig } from '@/lib/priority';
import type { TaskGenerationDTO } from '@/types/clickup';


interface Props {
  task: TaskGenerationDTO;
  onDelete: () => void;
  onUpdate: (updated: TaskGenerationDTO) => void; 
  structure: FolderWithListsMetadata[];        
  structureLoading: boolean;                   
  spaceId: string;    
  isVerificationFinished: boolean; 
  disabled: boolean; 
  isVerifying: boolean;
  showEstimation?: boolean;
}

export function GeneratedTaskCard({
  task,
  onDelete,
  onUpdate,
  structure,
  structureLoading,
  spaceId,
  isVerificationFinished,
  disabled,
  isVerifying,
  showEstimation = false,
}: Props) {
  const [expanded, setExpanded] = useState(false);
  const [locationOpen, setLocationOpen] = useState(false);
  const [showCreateList, setShowCreateList] = useState(false);
  const dropRef = useRef<HTMLDivElement>(null);
  const cfg = priorityConfig(task.task_priority);
  const options = buildLocationWithMetadataOptions(structure);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropRef.current && !dropRef.current.contains(e.target as Node))
        setLocationOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData('application/x-generated-task', JSON.stringify(task));
    e.dataTransfer.effectAllowed = 'copy';
  };

  return (
    <div className="bg-card border border-border/60 rounded-xl px-3 sm:px-4 py-3 sm:py-3.5 hover:border-border transition-colors group">
      <div className="flex items-start gap-2 sm:gap-3">
        <div
          draggable={isVerificationFinished && !disabled}
          onDragStart={isVerificationFinished && !disabled ? handleDragStart : undefined}
          className={`flex-shrink-0 mt-[3px] ${
            !disabled && isVerificationFinished ? 'cursor-grab active:cursor-grabbing' : 'cursor-default'
          }`}
        >
          <GripVertical className="w-4 h-4 text-muted-foreground/40 group-hover:text-muted-foreground" />
        </div>
        <div className={`w-2 h-2 rounded-full mt-[7px] flex-shrink-0 ${cfg.dot}`} />

          <div className="flex-1 min-w-0" onClick={() => setExpanded(p => !p)}>
            <p className="text-sm font-medium break-words">{task.task_name}</p>
            <p
              className={`text-sm text-muted-foreground mt-1 break-words ${
                expanded ? '' : 'line-clamp-2'
              }`}
            >
              {task.task_description}
            </p>

            <div className="flex items-center gap-2 mt-3 flex-wrap">
              {showEstimation && 'estimation' in task && (
                <span className="text-xs px-2 py-0.5 rounded-md border bg-blue-50 text-blue-700 border-blue-200 shrink-0">
                  {task.estimation} pts
                </span>
              )}

              <AssigneeAvatars value={task.task_assignee} />

              <span className={`text-xs px-2 py-0.5 rounded-md border shrink-0 ${
                task.task_priority?.trim() ? cfg.badge : 'bg-muted text-muted-foreground border-border'
              }`}>
                {task.task_priority?.trim() || 'No priority'}
              </span>

              <span className="text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground shrink-0">
                {task.task_status?.trim() || 'No status'}
              </span>

              <div ref={dropRef} className="relative" onClick={e => e.stopPropagation()}>
                <button
                  type="button"
                  disabled={disabled || isVerifying}
                  onClick={() => setLocationOpen(p => !p)}
                  className={`text-xs px-2 py-0.5 rounded-md border transition-colors max-w-[140px] sm:max-w-[200px] truncate block ${
                    task.location?.trim()
                      ? 'bg-muted/50 text-muted-foreground border-border hover:border-primary/40'
                      : 'bg-amber-50 text-amber-700 border-amber-200 hover:border-amber-400'
                  }`}
                >
                  {task.location?.trim() || '⚠ No location'}
                </button>

                {locationOpen && (
                  <div className="absolute z-50 mt-1 left-0 right-0 sm:right-auto sm:w-56 bg-popover border border-border rounded-md shadow-md max-h-52 overflow-y-auto">
                    {structureLoading ? (
                      <div className="px-3 py-2 text-xs text-muted-foreground">Loading…</div>
                    ) : options.length === 0 ? (
                      <div className="px-3 py-2 text-xs text-muted-foreground italic cursor-default">
                        {structure.length > 0 ? 'no list available' : 'no folder and no list available'}
                      </div>
                    ) : (
                      options.map(opt => (
                        <button
                          key={opt.listId}
                          type="button"
                          onClick={() => {
                            onUpdate({ ...task, location: opt.label });
                            setLocationOpen(false);
                          }}
                          disabled={disabled || isVerifying}
                          className={`w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors truncate ${
                            task.location === opt.label ? 'bg-muted font-medium' : ''
                          }`}
                        >
                          {opt.label}
                        </button>
                      ))
                    )}
                    <div className="border-t border-border">
                      <button
                        type="button"
                        onClick={() => { setLocationOpen(false); setShowCreateList(true); }}
                        disabled={disabled || isVerifying}
                        className="w-full text-left flex items-center gap-2 px-3 py-2 text-sm text-primary hover:bg-primary/5 font-medium"
                      >
                        <Plus className="w-3.5 h-3.5 shrink-0" />
                        Create new list…
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {showCreateList && createPortal(
                <CreateListForm
                  isOpen={showCreateList}
                  onClose={() => setShowCreateList(false)}
                  onSuccess={list => {
                    onUpdate({ ...task, location: list.name });
                    setShowCreateList(false);
                  }}
                  spaceId={spaceId}
                />,
                document.body
              )}
            </div>
          </div>

          <div className="flex items-center gap-1 flex-shrink-0">
            <Button
              variant="ghost"
              size="sm"
              disabled={disabled || isVerifying || isVerificationFinished}
              className="h-7 w-7 p-0"
              onClick={e => {
                e.stopPropagation();
                onDelete();
              }}
            >
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
      </div>
    </div>
  );
}