import { useEffect, useState } from 'react';
import type { CreateFolderRequest, FolderWithListsMetadata } from '@/api/api';
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
import { useClickUpStructure } from '@/hooks/clickup-structure-hooks/use-clikcup-structure';
import { useClickUpSpacesList } from '@/hooks/clickup-space-hooks/use-clickup-spaces';
import { useCreateFolder } from '@/hooks/clickup-structure-hooks/use-create-folder';
import { showSuccessToast } from '../global-toaster';

export interface CreateFolderFormProps {
  spaceId?: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (folder: FolderWithListsMetadata) => void;
}

export function CreateFolderForm({ spaceId, isOpen, onClose, onSuccess }: CreateFolderFormProps) {
  const { spaces, loading: spacesLoading } = useClickUpSpacesList();

  const [selectedSpaceId, setSelectedSpaceId] = useState<string>(spaceId || '');
  const { mutateAsync: createFolder, isPending } = useCreateFolder(selectedSpaceId); // 👈

  const [folderName, setFolderName] = useState('');

  const [errors, setErrors] = useState<Record<string, string>>({});

  const { structure, loading: structureLoading } = useClickUpStructure(selectedSpaceId);

  const existingFolderNames: string[] = structure
    .filter((folder) => folder.id !== (folder.lists?.[0]?.id ?? null))
    .map((folder) => folder.name);

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  useEffect(() => {
    if (isOpen) {
      setSelectedSpaceId(spaceId || '');
      setFolderName('');
      setErrors({});
    }
  }, [isOpen]);

  useEffect(() => {
    setErrors((e) => ({ ...e, name: '' }));
  }, [selectedSpaceId]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!selectedSpaceId) 
        newErrors.space = 'Please select a space';
    if (!folderName.trim()) {
      newErrors.name = 'Folder name is required';
    } else if (
      existingFolderNames.some(
        (n) => n.toLowerCase() === folderName.trim().toLowerCase(),
      )
    ) {
      newErrors.name = `"${folderName.trim()}" already exists in this space`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) 
        return;

    try {
      const request: CreateFolderRequest = {
        space_id: selectedSpaceId,
        name: folderName.trim(),
      };

      const result = await createFolder(request);

      if (!result) 
        return;

      showSuccessToast('Click Up folder created successfully');
      onSuccess?.(result);
      onClose();
    }finally{}
  };

  const isSaveDisabled =
    isPending || !selectedSpaceId || !folderName.trim() || structureLoading;

  if (!isOpen) 
    return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <Card className="w-full max-w-[420px] border-border shadow-2xl">
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-foreground">Create Folder</h2>
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
              <Label className="text-foreground font-medium">ClickUp Space</Label>
              <Select
                value={selectedSpaceId || 'none'}
                onValueChange={(v) => {
                  setSelectedSpaceId(v === 'none' ? '' : v);
                  setErrors((e) => ({ ...e, space: '' }));
                }}
                disabled={isPending || spacesLoading}
              >
                <SelectTrigger
                  className={`mt-2 bg-input w-full ${
                    errors.space ? 'border-destructive/70' : 'border-border'
                  } text-foreground`}
                >
                  <SelectValue placeholder={spacesLoading ? 'Loading spaces…' : 'No ClickUp space selected'} />
                </SelectTrigger>
                <SelectContent className="bg-card border-border w-full">
                  {spaces.length === 0 ? (
                    <SelectItem value="none" disabled>
                      No ClickUp space available
                    </SelectItem>
                  ) : (
                    <>
                    {spaces.map((space) => (
                      <SelectItem key={space.space_code} value={space.space_code || 'none'}>
                        {space.space_code}
                      </SelectItem>
                    ))}
                    </>
                  )}
                </SelectContent>
              </Select>
              {errors.space && (
                <div className="text-destructive text-xs mt-1 px-1">{errors.space}</div>
              )}
            </div>

            <div>
              <Label className="text-foreground font-medium">Folder Name</Label>
              <input
                type="text"
                placeholder="My Folder"
                value={folderName}
                onChange={(e) => {
                  setFolderName(e.target.value);
                  setErrors((err) => ({ ...err, name: '' }));
                }}
                className={inputClass(!!errors.name) + ' mt-2'}
                disabled={isPending}
              />
              {errors.name && (
                <div className="text-destructive text-xs mt-1 px-1">{errors.name}</div>
              )}
            </div>

            {selectedSpaceId && !structureLoading && existingFolderNames.length > 0 && (
              <div className="rounded-lg border border-border/60 bg-muted/30 px-3.5 py-2.5">
                <p className="text-xs text-muted-foreground font-medium mb-1.5">
                  Existing folders in this space:
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {existingFolderNames.map((name) => (
                    <span
                      key={name}
                      className="text-xs bg-muted rounded px-2 py-0.5 text-foreground/70 font-mono"
                    >
                      {name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {structureLoading && selectedSpaceId && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Loader2 className="w-3 h-3 animate-spin" />
                Checking existing folders…
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
                  Saving…
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Create Folder
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}