import { useEffect, useMemo, useState } from 'react';
import type { AddStatusRequest, ClickUpListMetadata } from '@/api/api';
import { StatusType } from '@/api/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CheckCircle2, Loader2, X } from 'lucide-react';
import { useClickUpStructure } from '@/hooks/use-clikcup_structure';
import { clickUpStructureCreationService } from '@/services/clickup-workspace-creation-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import { useNavigate } from 'react-router-dom';

export interface AddStatusFormProps {
  isOpen: boolean;
  spaceId: string;
  onClose: () => void;
  onSuccess?: (list: ClickUpListMetadata) => void;
}

interface ListOption {
  id: string;
  label: string;
  statuses: string[];
}

const STATUS_TYPE_LABELS: Record<StatusType, string> = {
  [StatusType.Open]: 'Open',
  [StatusType.Custom]: 'Custom',
  [StatusType.Closed]: 'Closed',
};

export function AddStatusForm({ isOpen, spaceId, onClose, onSuccess }: AddStatusFormProps) {
  const { structure, loading: structureLoading } = useClickUpStructure(spaceId);

  const [selectedListId, setSelectedListId] = useState<string>('');
  const [statusName, setStatusName] = useState('');
  const [color, setColor] = useState('#4f46e5');
  const [statusType, setStatusType] = useState<StatusType>(StatusType.Custom);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);

  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  const listOptions: ListOption[] = structure.flatMap((folder) => {
    const isFolderless = folder.id === (folder.lists?.[0]?.id ?? null);
    return (folder.lists ?? []).map((list) => ({
      id: list.id,
      label: isFolderless
        ? `${list.name} (${list.id})`
        : `${folder.name}/${list.name} (${list.id})`,
      statuses: list.statuses ?? [],
    }));
  });

  const selectedList = listOptions.find((l) => l.id === selectedListId);
  const existingStatuses = selectedList?.statuses ?? [];

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  useEffect(() => {
    if (isOpen) {
      setSelectedListId('');
      setStatusName('');
      setColor('#4f46e5');
      setStatusType(StatusType.Custom);
      setErrors({});
      setIsSaving(false);
    }
  }, [isOpen]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!selectedListId) 
        newErrors.list = 'Please select a list';
    if (!statusName.trim()) {
      newErrors.name = 'Status name is required';
    } else if (
      existingStatuses.some(
        (s) => s.toUpperCase() === statusName.trim().toUpperCase()
      )
    ) {
      newErrors.name = `"${statusName.trim().toUpperCase()}" already exists in this list`;
    }
    if (!color) newErrors.color = 'Color is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

const handleSave = async () => {
    if (!validate()) 
        return;

    setIsSaving(true);
    try {
      const request: AddStatusRequest = {
        list_id: selectedListId,
        status: statusName.trim().toUpperCase(),
        color,
        type: statusType,
      };

      const result = await withErrorHandling(
        () => clickUpStructureCreationService.addStatus(request),
        'Add status',
        onError,
      );

      if (!result) 
        return;

      onSuccess?.(result);
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  const isSaveDisabled =
    isSaving || !selectedListId || !statusName.trim() || !color;

  if (!isOpen) 
    return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <Card className="w-full max-w-[420px] border-border shadow-2xl">
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-foreground">Add Status to List</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              disabled={isSaving}
              className="h-8 w-8"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          <div className="space-y-4">
            <div>
              <Label className="text-foreground font-medium">ClickUp List</Label>
              <Select
                value={selectedListId || 'none'}
                onValueChange={(v) => {
                  setSelectedListId(v === 'none' ? '' : v);
                  setErrors((e) => ({ ...e, list: '' }));
                }}
                disabled={isSaving || structureLoading}
              >
                <SelectTrigger
                  className={`mt-2 bg-input w-full ${
                    errors.list ? 'border-destructive/70' : 'border-border'
                  } text-foreground`}
                >
                  <SelectValue
                    placeholder={
                      structureLoading ? 'Loading lists…' : 'Select a list…'
                    }
                  />
                </SelectTrigger>
                <SelectContent className="bg-card border-border w-full">
                  {listOptions.map((opt) => (
                    <SelectItem key={opt.id} value={opt.id}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.list && (
                <div className="text-destructive text-xs mt-1 px-1">{errors.list}</div>
              )}
            </div>

            <div>
              <Label className="text-foreground font-medium">Status Name</Label>
              <input
                type="text"
                placeholder="IN_REVIEW"
                value={statusName}
                onChange={(e) => {
                  setStatusName(e.target.value);
                  setErrors((err) => ({ ...err, name: '' }));
                }}
                className={inputClass(!!errors.name) + ' mt-2'}
                disabled={isSaving}
              />
              {statusName.trim() && (
                <p className="text-xs text-muted-foreground mt-1 px-1">
                  Will be saved as:{' '}
                  <span className="font-semibold text-foreground">
                    {statusName.trim().toUpperCase()}
                  </span>
                </p>
              )}
              {errors.name && (
                <div className="text-destructive text-xs mt-1 px-1">{errors.name}</div>
              )}
            </div>

            <div>
              <Label className="text-foreground font-medium">Color</Label>
              <div className="flex items-center gap-3 mt-2">
                <div
                  className="h-11 w-11 rounded-lg border border-border/60 shrink-0 cursor-pointer overflow-hidden"
                  style={{ backgroundColor: color }}
                >
                  <input
                    type="color"
                    value={color}
                    onChange={(e) => {
                      setColor(e.target.value);
                      setErrors((err) => ({ ...err, color: '' }));
                    }}
                    disabled={isSaving}
                    className="opacity-0 w-full h-full cursor-pointer"
                  />
                </div>
                <input
                  type="text"
                  value={color}
                  onChange={(e) => {
                    setColor(e.target.value);
                    setErrors((err) => ({ ...err, color: '' }));
                  }}
                  placeholder="#4f46e5"
                  className={inputClass(!!errors.color)}
                  disabled={isSaving}
                />
              </div>
              {errors.color && (
                <div className="text-destructive text-xs mt-1 px-1">{errors.color}</div>
              )}
            </div>

            <div>
              <Label className="text-foreground font-medium">Type</Label>
              <Select
                value={statusType}
                onValueChange={(v) => setStatusType(v as StatusType)}
                disabled={isSaving}
              >
                <SelectTrigger className="mt-2 bg-input border-border text-foreground w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-card border-border w-full">
                  {Object.values(StatusType).map((t) => (
                    <SelectItem key={t} value={t}>
                      {STATUS_TYPE_LABELS[t]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedList && existingStatuses.length > 0 && (
              <div className="rounded-lg border border-border/60 bg-muted/30 px-3.5 py-2.5">
                <p className="text-xs text-muted-foreground font-medium mb-1.5">
                  Existing statuses in this list:
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {existingStatuses.map((s) => (
                    <span
                      key={s}
                      className="text-xs bg-muted rounded px-2 py-0.5 text-foreground/70 font-mono"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-2 pt-4 border-t border-border">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isSaving}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              className="flex-1 gap-2"
              disabled={isSaveDisabled}
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving…
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Add Status
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}