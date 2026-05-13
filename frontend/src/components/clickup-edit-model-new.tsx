import { useEffect, useState } from 'react';
import type {
  ClickUpSpaceLightDTO,
  ClickUpSpaceUpdateDTO,
  ClickUpSpaceRegisterDTO,
  CreateSpaceRequest,
  GitRepoDetailDTO,
  AssociateClickUpSpaceRequest,
} from '@/api/api';
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
import { CheckCircle2, Database, Loader2, Plus, X } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';

export interface ClickUpEditModalProps {
  isOpen: boolean;
  repositories: GitRepoDetailDTO[];
  editingSpace: ClickUpSpaceLightDTO | null;
  onClose: () => void;
  onCreate: (space: CreateSpaceRequest) => Promise<boolean>;
  onRegister: (space: ClickUpSpaceRegisterDTO) => Promise<boolean | undefined>;
  onUpdate: (space: ClickUpSpaceUpdateDTO) => Promise<boolean>;
  showNotFoundDialog?: boolean;
  onNotFoundDialogChange?: (show: boolean) => void;
  showNameMismatchDialog?: boolean;
  onNameMismatchDialogChange?: (show: boolean) => void;
  onAssociate: (association: AssociateClickUpSpaceRequest) => Promise<boolean>;
  refreshSpaces?: () => void;
}

export type CreationMode = 'create' | 'register';

export function ClickUpEditModal({
  isOpen,
  repositories,
  editingSpace,
  onClose,
  onCreate,
  onRegister,
  onUpdate,
  showNotFoundDialog,
  onNotFoundDialogChange,
  showNameMismatchDialog,
  onNameMismatchDialogChange,
  onAssociate,
  refreshSpaces,
}: ClickUpEditModalProps) {
  const [formData, setFormData] = useState<Partial<ClickUpSpaceLightDTO>>({});
  const [errors, setErrors]     = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [creationMode, setCreationMode] = useState<CreationMode | null>(null);

  const repoOptions = repositories.filter(
    (repo): repo is GitRepoDetailDTO & { id: number } =>
      typeof repo.id === 'number' && repo.clickup_space === null,
  );

  const hasChanges = editingSpace
    ? formData.name !== editingSpace.name ||
      formData.space_code !== editingSpace.space_code ||
      formData.repo?.id !== editingSpace.repo?.id
    : true;

  const isCancelDisabled = isSaving;

  const isSaveDisabled = (() => {
    if (isSaving) 
      return true;
    if (editingSpace) 
      return !hasChanges;
    if (!creationMode) 
      return true;
    if (creationMode === 'create' && !formData.name?.trim()) 
      return true;
    if (creationMode === 'register' && !formData.name?.trim() && !formData.space_code?.trim()) 
       return true;
    return false;
  })();

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  const handleRepoChange = (repoId: string) => {
    if (repoId === 'none') {
      setFormData((prev) => ({ ...prev, repo: null }));
    } else {
      const selected = repoOptions.find((r) => r.id?.toString() === repoId);
      setFormData((prev) => ({
        ...prev,
        repo: selected
          ? { id: selected.id ?? null, name: selected.name ?? null, url: selected.url ?? null }
          : null,
      }));
    }
  };

  useEffect(() => {
    if (isOpen) {
      setErrors({});
      setIsSaving(false);
      setCreationMode(null);
      setFormData(editingSpace ? { ...editingSpace } : { name: '', space_code: '', repo: null });
    }
  }, [isOpen, editingSpace]);

  const handleModeChange = (mode: CreationMode) => {
    setCreationMode(mode);
    setErrors({});
    setFormData((prev) => ({ ...prev, name: '', space_code: '', repo: null }));
  };

  const validate = (): boolean => {
    setErrors({});
    const newErrors: Record<string, string> = {};
    if (!formData.name?.trim()) 
        newErrors.name = 'Space name is required';

    if ((editingSpace || creationMode === 'register') &&!formData.space_code?.trim()) 
      newErrors.space_code = 'Space ID is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSaveOrUpdate = async () => {
    if (!validate()) 
      return;
    
    setIsSaving(true);
    let success: boolean | undefined = false;
    try {
      if (editingSpace) {
        success = await onUpdate({ ...editingSpace, ...formData } as ClickUpSpaceUpdateDTO);
      } else {
        if (creationMode === 'register') {
          success = await onRegister({
            name: formData.name!,
            space_code: formData.space_code!,
            ignore_name: false,
          } as ClickUpSpaceRegisterDTO);
        } else {
          success = await onCreate({ space_name: formData.name! } as CreateSpaceRequest);
        }

        if (success && formData.repo) {
          const payload: AssociateClickUpSpaceRequest = {
            space_code: formData.space_code!,
            repo_url: formData.repo?.url!,
          };
          success = await onAssociate(payload);
        }
      }

      if (success) {
        onClose();
        refreshSpaces?.();
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleNotFoundConfirm = async () => {
    onNotFoundDialogChange?.(false);
    setIsSaving(true);
    try {
      let success = false;
      success = await onCreate({ space_name: formData.space_code! } as CreateSpaceRequest);
      if (success && formData.repo) {
          const payload: AssociateClickUpSpaceRequest = {
            space_code: formData.space_code!,
            repo_url: formData.repo?.url!,
          };
          success = await onAssociate(payload);
      }
      if (success) {
        onClose();
        refreshSpaces?.();
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleNotFoundCancel = () => {
    onNotFoundDialogChange?.(false);
    onClose();
  };

  const handleNameMismatchConfirm = async () => {
    onNameMismatchDialogChange?.(false);
    setIsSaving(true);
    try {
      let success: boolean | undefined = false;
      success = await onRegister({
        name: formData.name!,
        space_code: formData.space_code!,
        ignore_name: true,
      } as ClickUpSpaceRegisterDTO);
      if (success && formData.repo) {
          const payload: AssociateClickUpSpaceRequest = {
            space_code: formData.space_code!,
            repo_url: formData.repo?.url!,
          };
          success = await onAssociate(payload);
      }
      if (success) {
        onClose();
        refreshSpaces?.();
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleNameMismatchCancel = () => {
    onNameMismatchDialogChange?.(false);
  };

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-[420px] border-border shadow-2xl">
            <div className="p-6 space-y-6">

              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-foreground">
                  {editingSpace ? 'Edit ClickUp Space' : 'Add New ClickUp Space'}
                </h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  disabled={isCancelDisabled}
                  className="h-8 w-8"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>

              {editingSpace && (
                <div className="space-y-4">
                  <div>
                    <Label className="text-foreground font-medium">Space Name</Label>
                    <input
                      type="text"
                      placeholder="My ClickUp Space"
                      value={formData.name || ''}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className={inputClass(!!errors.name) + ' mt-2'}
                      disabled={isSaving}
                    />
                    {errors.name && (
                      <p className="text-destructive text-xs mt-1 px-1">{errors.name}</p>
                    )}
                  </div>

                  <div>
                    <Label className="text-foreground font-medium">Space ID</Label>
                    <input
                      type="text"
                      placeholder="cus_prod_001"
                      value={formData.space_code || ''}
                      onChange={(e) => setFormData({ ...formData, space_code: e.target.value })}
                      className={inputClass(!!errors.space_code) + ' mt-2'}
                      disabled={isSaving}
                    />
                    {errors.space_code && (
                      <p className="text-destructive text-xs mt-1 px-1">{errors.space_code}</p>
                    )}
                  </div>

                  <div>
                    <Label className="text-foreground font-medium">Linked Repository</Label>
                    <Select
                      value={formData.repo?.id?.toString() || 'none'}
                      onValueChange={handleRepoChange}
                      disabled={isSaving}
                    >
                      <SelectTrigger className="mt-2 bg-input border-border text-foreground w-full">
                        <SelectValue placeholder="Select a repository..." />
                      </SelectTrigger>
                      <SelectContent className="bg-card border-border w-full">
                        {repositories.length === 0 ? (
                          <SelectItem value="none" disabled>No repository available</SelectItem>
                        ) :  repoOptions.length === 0 ? (
                          <SelectItem value="none" disabled>No repository available for association (all are already linked)</SelectItem>
                        ) : (
                          <>
                            <SelectItem value="none" className="text-muted-foreground hidden" disabled>
                              No repository selected
                            </SelectItem>
                            {repoOptions.map((repo, i) => (
                              <SelectItem key={repo.id ?? repo.url ?? i} value={repo.id.toString()}>
                                {repo.url ?? 'Unknown repo'} ({repo.name ?? 'Unnamed'})
                              </SelectItem>
                            ))}
                          </>
                        )}
                      </SelectContent>
                    </Select>
                    {formData.repo?.name && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Selected: <span className="font-semibold">{formData.repo.name}</span>
                      </p>
                    )}
                  </div>
                </div>
              )}

              {!editingSpace && (
                <div className="space-y-4">

                  <div className="space-y-2">
                    <Label className="text-foreground font-medium">Mode</Label>
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      <button
                        type="button"
                        disabled={isSaving}
                        onClick={() => handleModeChange('create')}
                        className={`flex flex-col items-center gap-1.5 rounded-lg border p-3 text-sm transition-colors cursor-pointer
                          ${creationMode === 'create'
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-border bg-muted/40 text-muted-foreground hover:bg-muted/80'
                          }`}
                      >
                        <Plus className="w-5 h-5" />
                        <span className="font-medium">Create &amp; Save</span>
                        <span className="text-xs text-center leading-snug opacity-70">
                          Create in ClickUp then persist in DB
                        </span>
                      </button>

                      <button
                        type="button"
                        disabled={isSaving}
                        onClick={() => handleModeChange('register')}
                        className={`flex flex-col items-center gap-1.5 rounded-lg border p-3 text-sm transition-colors cursor-pointer
                          ${creationMode === 'register'
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-border bg-muted/40 text-muted-foreground hover:bg-muted/80'
                          }`}
                      >
                        <Database className="w-5 h-5" />
                        <span className="font-medium">Register Only</span>
                        <span className="text-xs text-center leading-snug opacity-70">
                          Verify &amp; save existing ClickUp space
                        </span>
                      </button>
                    </div>
                  </div>

                  {creationMode === 'create' && (
                    <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
                      <div>
                        <Label className="text-foreground font-medium">Space Name</Label>
                        <input
                          type="text"
                          placeholder="My ClickUp Space"
                          value={formData.name || ''}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          className={inputClass(!!errors.name) + ' mt-2'}
                          disabled={isSaving}
                        />
                        {errors.name && (
                          <p className="text-destructive text-xs mt-1 px-1">{errors.name}</p>
                        )}
                      </div>

                      <div>
                        <Label className="text-foreground font-medium">Linked Repository</Label>
                        <Select
                          value={formData.repo?.id?.toString() || 'none'}
                          onValueChange={handleRepoChange}
                          disabled={isSaving}
                        >
                          <SelectTrigger className="mt-2 bg-input border-border text-foreground w-full">
                            <SelectValue placeholder="Select a repository..." />
                          </SelectTrigger>
                          <SelectContent className="bg-card border-border w-full">
                            {repoOptions.length === 0 ? (
                              <SelectItem value="none" disabled>No repository available</SelectItem>
                            ) : (
                              <>
                                <SelectItem value="none" className="text-muted-foreground hidden" disabled>
                                  No repository selected
                                </SelectItem>
                                {repoOptions.map((repo, i) => (
                                  <SelectItem key={repo.id ?? repo.url ?? i} value={repo.id.toString()}>
                                    {repo.url ?? 'Unknown repo'} ({repo.name ?? 'Unnamed'})
                                  </SelectItem>
                                ))}
                              </>
                            )}
                          </SelectContent>
                        </Select>
                        {formData.repo?.name && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Selected: <span className="font-semibold">{formData.repo.name}</span>
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {creationMode === 'register' && (
                    <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
                      <div>
                        <Label className="text-foreground font-medium">Space ID</Label>
                        <input
                          type="text"
                          placeholder="cus_prod_001"
                          value={formData.space_code || ''}
                          onChange={(e) => setFormData({ ...formData, space_code: e.target.value })}
                          className={inputClass(!!errors.space_code) + ' mt-2'}
                          disabled={isSaving}
                        />
                        {errors.space_code && (
                          <p className="text-destructive text-xs mt-1 px-1">{errors.space_code}</p>
                        )}
                      </div>

                      <div>
                        <Label className="text-foreground font-medium">Space Name</Label>
                        <input
                          type="text"
                          placeholder="My ClickUp Space"
                          value={formData.name || ''}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          className={inputClass(!!errors.name) + ' mt-2'}
                          disabled={isSaving}
                        />
                        {errors.name && (
                          <p className="text-destructive text-xs mt-1 px-1">{errors.name}</p>
                        )}
                      </div>

                      <div>
                        <Label className="text-foreground font-medium">Linked Repository</Label>
                        <Select
                          value={formData.repo?.id?.toString() || 'none'}
                          onValueChange={handleRepoChange}
                          disabled={isSaving}
                        >
                          <SelectTrigger className="mt-2 bg-input border-border text-foreground w-full">
                            <SelectValue placeholder="Select a repository..." />
                          </SelectTrigger>
                          <SelectContent className="bg-card border-border w-full">
                            {repoOptions.length === 0 ? (
                              <SelectItem value="none" disabled>No repository available</SelectItem>
                            ) : (
                              <>
                                <SelectItem value="none" className="text-muted-foreground hidden" disabled>
                                  No repository selected
                                </SelectItem>
                                {repoOptions.map((repo, i) => (
                                  <SelectItem key={repo.id ?? repo.url ?? i} value={repo.id.toString()}>
                                    {repo.url ?? 'Unknown repo'} ({repo.name ?? 'Unnamed'})
                                  </SelectItem>
                                ))}
                              </>
                            )}
                          </SelectContent>
                        </Select>
                        {formData.repo?.name && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Selected: <span className="font-semibold">{formData.repo.name}</span>
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div className="flex gap-2 pt-4 border-t border-border">
                <Button
                  variant="outline"
                  onClick={onClose}
                  disabled={isCancelDisabled}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSaveOrUpdate}
                  className="flex-1 gap-2"
                  disabled={isSaveDisabled}
                >
                  {isSaving ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      {editingSpace ? 'Update' : 'Save'} Space
                    </>
                  )}
                </Button>
              </div>

            </div>
          </Card>
        </div>
      )}

      <Dialog
        open={!!showNotFoundDialog}
        onOpenChange={(open) => { if (!open) handleNotFoundCancel(); }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Space not found in ClickUp</DialogTitle>
            <DialogDescription>
              The space <span className="font-semibold">{formData.space_code}</span> does not exist
              in ClickUp yet. Would you like to create it in ClickUp and save it to the database?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={handleNotFoundCancel} disabled={isSaving}>
              No, cancel
            </Button>
            <Button onClick={handleNotFoundConfirm} disabled={isSaving} className="gap-2">
              {isSaving && <Loader2 className="w-4 h-4 animate-spin" />}
              Yes, create it
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={!!showNameMismatchDialog}
        onOpenChange={(open) => { if (!open) handleNameMismatchCancel(); }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Space name mismatch</DialogTitle>
            <DialogDescription>
              The space <span className="font-semibold">{formData.space_code}</span> exists in
              ClickUp but its name differs from what you entered (
              <span className="font-semibold">{formData.name}</span>). Would you like to register
              it using the real ClickUp name instead?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={handleNameMismatchCancel} disabled={isSaving}>
              No, let me correct it
            </Button>
            <Button onClick={handleNameMismatchConfirm} disabled={isSaving} className="gap-2">
              {isSaving && <Loader2 className="w-4 h-4 animate-spin" />}
              Yes, use real name
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
