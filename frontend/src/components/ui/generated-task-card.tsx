import { useEffect, useRef, useState } from 'react';
import { Trash2, GripVertical, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { FolderWithListsMetadata, GeneratedTask } from '@/api/api';
import { AssigneeAvatars } from '../ui/assignees-avatar';
import { buildLocationOptions } from './location-field';
import { CreateListForm } from './create-list-form';

const PRIORITY_CONFIG: Record<string, { badge: string; dot: string }> = {
  urgent: { badge: 'bg-red-50 text-red-700 border-red-100', dot: 'bg-red-500' },
  high: { badge: 'bg-amber-50 text-amber-700 border-amber-100', dot: 'bg-amber-500' },
  medium: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  normal: { badge: 'bg-blue-50 text-blue-700 border-blue-100', dot: 'bg-blue-500' },
  low: { badge: 'bg-muted text-muted-foreground border-border', dot: 'bg-muted-foreground' },
};

function priorityConfig(p: string) {
  return PRIORITY_CONFIG[p?.toLowerCase()] ?? PRIORITY_CONFIG['normal'];
}

interface Props {
  task: GeneratedTask;
  onDelete: () => void;
  onUpdate: (updated: GeneratedTask) => void; 
  structure: FolderWithListsMetadata[];        
  structureLoading: boolean;                   
  spaceId: string;    
  draggable: boolean; 
  disabled: boolean;                        
}

export function GeneratedTaskCard({
  task,
  onDelete,
  onUpdate,
  structure,
  structureLoading,
  spaceId,
  draggable,
  disabled 
}: Props) {
  const [expanded, setExpanded] = useState(false);
  const [locationOpen, setLocationOpen] = useState(false);
  const [showCreateList, setShowCreateList] = useState(false);
  const dropRef = useRef<HTMLDivElement>(null);
  const cfg = priorityConfig(task.task_priority);
  const options = buildLocationOptions(structure);

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
    <div className="bg-card border border-border/60 rounded-xl px-4 py-3.5 hover:border-border transition-colors group">
      <div className="flex items-start gap-3">
        <div
          draggable={draggable && !disabled}
          onDragStart={draggable && !disabled ? handleDragStart : undefined}
          className={`flex-shrink-0 mt-[3px] ${
            !disabled && draggable ? 'cursor-grab active:cursor-grabbing' : 'cursor-default'
          }`}
        >
          <GripVertical className="w-4 h-4 text-muted-foreground/40 group-hover:text-muted-foreground" />
        </div>
        <div className={`w-2 h-2 rounded-full mt-[7px] ${cfg.dot}`} />

          <div className="flex-1 min-w-0" onClick={() => setExpanded(p => !p)}>
            <p className="text-sm font-medium">{task.task_name}</p>

            <p
              className={`text-sm text-muted-foreground mt-1 ${
                expanded ? '' : 'line-clamp-2'
              }`}
            >
              {task.task_description}
            </p>

            <div className="flex items-center gap-3 mt-3 flex-wrap">
              <AssigneeAvatars value={task.task_assigne} />

              <span className={`text-xs px-2 py-0.5 rounded-md border ${
                task.task_priority?.trim() ? cfg.badge : 'bg-muted text-muted-foreground border-border'
              }`}>
                {task.task_priority?.trim() || 'No priority'}
              </span>

              <span className="text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground">
                {task.task_status?.trim() || 'No status'}
              </span>

              <div ref={dropRef} className="relative" onClick={e => e.stopPropagation()}>
                <button
                  type="button"
                  disabled={disabled}
                  onClick={() => setLocationOpen(p => !p)}
                  className={`text-xs px-2 py-0.5 rounded-md border transition-colors ${
                    task.location?.trim()
                      ? 'bg-muted/50 text-muted-foreground border-border hover:border-primary/40'
                      : 'bg-amber-50 text-amber-700 border-amber-200 hover:border-amber-400'
                  }`}
                >
                  {task.location?.trim() || '⚠ No location'}
                </button>

                {locationOpen && (
                  <div className="absolute z-50 mt-1 left-0 w-56 bg-popover border border-border rounded-md shadow-md max-h-52 overflow-y-auto">
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
                          disabled={disabled}
                          className={`w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors ${
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
                        disabled={disabled}
                        className="w-full text-left flex items-center gap-2 px-3 py-2 text-sm text-primary hover:bg-primary/5 font-medium"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        Create new list…
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {showCreateList && (
                <CreateListForm
                  isOpen={showCreateList}
                  onClose={() => setShowCreateList(false)}
                  onSuccess={list => {
                    onUpdate({ ...task, location: list.name });
                    setShowCreateList(false);
                    
                  }}
                  spaceId={spaceId}
                />
              )}
            </div>
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              disabled={disabled}
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