import { useEffect, useMemo, useState } from 'react';
import type { ClickUpListMetadata } from '@/api/api';
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
import { CheckCircle2, Loader2, X, List, FolderOpen, FolderPlus } from 'lucide-react';
import { useClickUpStructure } from '@/hooks/clickup-structure-hooks/use-clikcup-structure';
import { useCreateList } from '@/hooks/clickup-structure-hooks/use-create-list';
import { useCreateFolder } from '@/hooks/clickup-structure-hooks/use-create-folder';
import { showSuccessToast } from '../global-toaster';

export interface CreateListFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (list: ClickUpListMetadata) => void;
  spaceId: string;
}

type PlacementMode = 'direct' | 'existing-folder' | 'new-folder';

const PLACEMENT_OPTIONS: { value: PlacementMode; label: string; description: string; icon: React.ReactNode }[] = [
  {
    value: 'direct',
    label: 'Direct in space',
    description: 'Create list directly at the space level',
    icon: <List className="w-4 h-4" />,
  },
  {
    value: 'existing-folder',
    label: 'In existing folder',
    description: 'Place list inside an existing folder',
    icon: <FolderOpen className="w-4 h-4" />,
  },
  {
    value: 'new-folder',
    label: 'In a new folder',
    description: 'Create a new folder, then add the list inside',
    icon: <FolderPlus className="w-4 h-4" />,
  },
];

export function CreateListForm({ isOpen, onClose, onSuccess, spaceId }: CreateListFormProps) {
  const [selectedSpaceId, setSelectedSpaceId] = useState<string>(spaceId);

  const { mutateAsync: createFolder, isPending: isFolderPending } = useCreateFolder(selectedSpaceId); 
  const { mutateAsync: createList, isPending: isListPending  } = useCreateList(selectedSpaceId);    
  const isPending = isFolderPending || isListPending;

  const [placementMode, setPlacementMode] = useState<PlacementMode>('direct');
  const [listName, setListName] = useState('');
  const [selectedFolderId, setSelectedFolderId] = useState<string>('');
  const [newFolderName, setNewFolderName] = useState('');

  const [errors, setErrors] = useState<Record<string, string>>({});

  const { structure, loading: structureLoading } = useClickUpStructure(selectedSpaceId);
  
  const existingFolders = structure.filter(
    (folder) => folder.id !== (folder.lists?.[0]?.id ?? null),
  );

  const hasFolders = !structureLoading && selectedSpaceId && existingFolders.length > 0;

  const availablePlacementOptions = PLACEMENT_OPTIONS.filter(
    (opt) => opt.value !== 'existing-folder' || hasFolders,
  );

  const existingFolderNames = existingFolders.map((f) => f.name);

  const existingListNames: string[] = useMemo(() => {
    if (placementMode === 'direct') {
      return structure
        .filter((folder) => folder.id === (folder.lists?.[0]?.id ?? null))
        .flatMap((folder) => folder.lists ?? [])
        .map((l) => l.name);
    }
    if (placementMode === 'existing-folder' && selectedFolderId) {
      const folder = existingFolders.find((f) => f.id === selectedFolderId);
      return (folder?.lists ?? []).map((l) => l.name);
    }
    return [];
  }, [placementMode, structure, selectedFolderId]);

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  useEffect(() => {
    if (isOpen) {
      setPlacementMode('direct');
      setSelectedSpaceId(spaceId);
      setListName('');
      setSelectedFolderId('');
      setNewFolderName('');
      setErrors({});
    }
  }, [isOpen]);

  useEffect(() => {
    if (placementMode === 'existing-folder' && !hasFolders && !structureLoading) {
      setPlacementMode('direct');
    }
  }, [hasFolders, structureLoading, placementMode]);

  useEffect(() => {
    setSelectedFolderId('');
    setNewFolderName('');
    setErrors((e) => ({ ...e, folder: '', newFolder: '', name: '' }));
  }, [placementMode, selectedSpaceId]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!selectedSpaceId) 
        newErrors.space = 'Please select a space';

    if (!listName.trim()) {
      newErrors.name = 'List name is required';
    } else if (
      existingListNames.some((n) => n.toLowerCase() === listName.trim().toLowerCase())
    ) {
      newErrors.name = `"${listName.trim()}" already exists in this location`;
    }

    if (placementMode === 'existing-folder' && !selectedFolderId) {
      newErrors.folder = 'Please select a folder';
    }

    if (placementMode === 'new-folder') {
      if (!newFolderName.trim()) {
        newErrors.newFolder = 'Folder name is required';
      } else if (
        existingFolderNames.some(
          (n) => n.toLowerCase() === newFolderName.trim().toLowerCase(),
        )
      ) {
        newErrors.newFolder = `"${newFolderName.trim()}" already exists in this space`;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) 
        return;
    
    let folderId: string | null = null;
    let folderName: string | undefined;

    if (placementMode === 'new-folder') {
      const createdFolder = await createFolder({
        space_id: selectedSpaceId,
        name: newFolderName.trim(),
      });
      if (!createdFolder) 
        return;

      showSuccessToast('Click Up folder created successfully');
      folderId = createdFolder.id;
      folderName = newFolderName.trim();
    } else if (placementMode === 'existing-folder') {
      folderId = selectedFolderId;
      folderName = existingFolders.find(f => f.id === selectedFolderId)?.name; 
    }

    const result = await createList({ 
      space_id: selectedSpaceId,
      name: listName.trim(),
      folder_id: folderId,
    });

    if (!result) 
      return;

    showSuccessToast('Click Up list added successfully');

    const enrichedResult: ClickUpListMetadata = folderName
    ? { ...result, name: `${folderName} / ${result.name}` }
    : result;

    onSuccess?.(enrichedResult);

    onClose();
  } 

  const isSaveDisabled =
    isPending ||
    selectedSpaceId === null ||
    selectedSpaceId === '' ||
    !listName.trim() ||
    (placementMode === 'existing-folder' && !selectedFolderId) ||
    (placementMode === 'new-folder' && !newFolderName.trim());

  const savingLabel =
    placementMode === 'new-folder' ? 'Creating folder & list…' : 'Creating list…';

  if (!isOpen) 
    return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <Card className="w-full max-w-[440px] border-border shadow-2xl">
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-foreground">Create Click Up List</h2>
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
              <Label className="text-foreground font-medium">Placement</Label>
              <div className={`mt-2 grid gap-2 ${availablePlacementOptions.length === 2 ? 'grid-cols-2' : 'grid-cols-3'}`}>
                {availablePlacementOptions.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    disabled={isPending}
                    onClick={() => setPlacementMode(opt.value)}
                    className={`flex flex-col items-center gap-1.5 rounded-lg border px-2 py-3 text-center transition cursor-pointer
                      ${
                        placementMode === opt.value
                          ? 'border-foreground/40 bg-muted text-foreground'
                          : 'border-border/60 bg-muted/30 text-muted-foreground hover:border-foreground/20 hover:text-foreground'
                      }
                    `}
                  >
                    {opt.icon}
                    <span className="text-xs font-medium leading-tight">{opt.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {placementMode === 'existing-folder' && (
              <div>
                <Label className="text-foreground font-medium">Folder</Label>
                <Select
                  value={selectedFolderId || undefined }
                  onValueChange={(v) => {
                    setSelectedFolderId(v);
                    setErrors((e) => ({ ...e, folder: '' }));
                  }}
                  disabled={isPending || structureLoading || !selectedSpaceId}
                >
                  <SelectTrigger
                    className={`mt-2 bg-input w-full ${
                      errors.folder ? 'border-destructive/70' : 'border-border'
                    } text-foreground`}
                  >
                    <SelectValue
                      placeholder={
                        !selectedSpaceId
                          ? 'Select a space first…'
                          : structureLoading
                          ? 'Loading folders…'
                          : existingFolders.length === 0
                          ? 'No folders found'
                          : 'No folder selected'
                      }
                    />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border w-full">
                    {existingFolders.length === 0 ? (
                      <SelectItem value="none" disabled>
                        No folder available
                      </SelectItem>
                    ) : (
                      <>
                      {existingFolders.map((folder) => (
                        <SelectItem key={folder.id} value={folder.id}>
                          {folder.name}
                        </SelectItem>
                      ))}
                      </>
                    )}
                  </SelectContent>
                </Select>
                {errors.folder && (
                  <div className="text-destructive text-xs mt-1 px-1">{errors.folder}</div>
                )}
              </div>
            )}

            {placementMode === 'new-folder' && (
              <div>
                <Label className="text-foreground font-medium">New Folder Name</Label>
                <input
                  type="text"
                  placeholder="My Folder"
                  value={newFolderName}
                  onChange={(e) => {
                    setNewFolderName(e.target.value);
                    setErrors((err) => ({ ...err, newFolder: '' }));
                  }}
                  className={inputClass(!!errors.newFolder) + ' mt-2'}
                  disabled={isPending}
                />
                {errors.newFolder && (
                  <div className="text-destructive text-xs mt-1 px-1">{errors.newFolder}</div>
                )}
                {selectedSpaceId && !structureLoading && existingFolderNames.length > 0 && (
                  <div className="rounded-lg border border-border/60 bg-muted/30 px-3.5 py-2.5 mt-2">
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
              </div>
            )}

            <div>
              <Label className="text-foreground font-medium">List Name</Label>
              <input
                type="text"
                placeholder="My List"
                value={listName}
                onChange={(e) => {
                  setListName(e.target.value);
                  setErrors((err) => ({ ...err, name: '' }));
                }}
                className={inputClass(!!errors.name) + ' mt-2'}
                disabled={isPending}
              />
              {errors.name && (
                <div className="text-destructive text-xs mt-1 px-1">{errors.name}</div>
              )}
            </div>

            {structureLoading && selectedSpaceId && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Loader2 className="w-3 h-3 animate-spin" />
                Loading space structure…
              </div>
            )}

            {placementMode === 'new-folder' && (
              <div className="rounded-lg border border-border/60 bg-muted/30 px-3.5 py-2.5">
                <p className="text-xs text-muted-foreground">
                  <span className="font-semibold text-foreground">2-step creation:</span>{' '}
                  the folder will be created first, then the list will be added inside it.
                </p>
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
                  {savingLabel}
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Create List
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}