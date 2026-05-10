import { useEffect, useState, useCallback } from 'react';
import type { ClickUpSpaceDTO, CreateSpaceRequest } from '@/api/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { CheckCircle2, Loader2, X } from 'lucide-react';
import { useClickUpSpacesList } from '@/hooks/clickup-structure-hooks/use-clickup-spaces';
import { useCreateSpace } from '@/hooks/clickup-structure-hooks/use-create-space';
import { showSuccessToast } from '../global-toaster';

export interface CreateSpaceFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (space: ClickUpSpaceDTO) => void;
}

export function CreateSpaceForm({ isOpen, onClose, onSuccess }: CreateSpaceFormProps) {
  const { spaces, loading: spacesLoading } = useClickUpSpacesList();
  const { mutateAsync: createSpace, isPending } = useCreateSpace();
  
  const [spaceName, setSpaceName] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  useEffect(() => {
    if (isOpen) {
      setSpaceName('');
      setErrors({});
    }
  }, [isOpen]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    const trimmed = spaceName.trim();

    if (!trimmed) {
      newErrors.name = 'Space name is required';
    } else {
      const alreadyExists = spaces.some(
        (s) => s.name?.toUpperCase() === trimmed.toUpperCase(),
      );
      if (alreadyExists) {
        newErrors.name = `"${trimmed}" already exists — please choose a different name`;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = useCallback(async () => {
    if (!validate()) 
        return;
    
    try {
      const request: CreateSpaceRequest = {
        space_id: spaceName.trim(),
      };

      const result = await createSpace(request);

      if (!result) 
        return;

      showSuccessToast('Click Up space created successfully');
      onSuccess?.(result);
      onClose();
    } finally {}
  }, [spaceName, spaces, onSuccess, onClose]);

  const isSaveDisabled = isPending || spacesLoading || !spaceName.trim();

  if (!isOpen) 
    return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <Card className="w-full max-w-[420px] border-border shadow-2xl">
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-foreground">Create Click up Space</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              disabled={isPending}
              className="h-8 w-8"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          <div className="space-y-4">
            <div>
              <Label className="text-foreground font-medium">Space Name</Label>
              <input
                type="text"
                placeholder="my-space"
                value={spaceName}
                onChange={(e) => {
                  setSpaceName(e.target.value);
                  setErrors((err) => ({ ...err, name: '' }));
                }}
                className={inputClass(!!errors.name) + ' mt-2'}
                disabled={isPending}
              />
              {spaceName.trim() && !errors.name && (
                <p className="text-xs text-muted-foreground mt-1 px-1">
                  Will be created as:{' '}
                  <span className="font-semibold text-foreground">
                    {spaceName.trim()}
                  </span>
                </p>
              )}
              {errors.name && (
                <div className="text-destructive text-xs mt-1 px-1">{errors.name}</div>
              )}
            </div>

            {spaces.length > 0 && (
              <div className="rounded-lg border border-border/60 bg-muted/30 px-3.5 py-2.5">
                <p className="text-xs text-muted-foreground font-medium mb-1.5">
                  Existing spaces:
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {spaces.map((s) => (
                    <span
                      key={s.id}
                      className="text-xs bg-muted rounded px-2 py-0.5 text-foreground/70 font-mono"
                    >
                      {s.name}
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
              disabled={isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              className="flex-1 gap-2"
              disabled={isSaveDisabled}
            >
              {isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating…
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Create Space
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}