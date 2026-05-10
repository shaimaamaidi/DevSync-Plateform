import { useEffect, useState } from 'react';
import type { ClickUpSpaceLightDTO, ClickUpSpaceCreateDTO, ClickUpSpaceUpdateDTO, GitRepoDTO } from '@/api/api';
import { repoService } from '@/services/repo-service';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CheckCircle2, Loader2, X } from 'lucide-react';

export interface ClickUpEditModalProps {
  isOpen: boolean;
  editingSpace: ClickUpSpaceLightDTO | null;
  onClose: () => void;
  onAdd: (space: ClickUpSpaceCreateDTO) => Promise<boolean>;
  onUpdate: (space: ClickUpSpaceUpdateDTO) => Promise<boolean>;
}

export function ClickUpEditModal({ isOpen, editingSpace, onClose, onAdd, onUpdate }: ClickUpEditModalProps) {
  const [formData, setFormData] = useState<Partial<ClickUpSpaceLightDTO>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [repos, setRepos] = useState<GitRepoDTO[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  const repoOptions = repos.filter(
    (repo): repo is GitRepoDTO & { id: number } => typeof repo.id === 'number'
  );

  const hasChanges = editingSpace
    ? (
      formData.name !== editingSpace.name ||
      formData.space_code !== editingSpace.space_code ||
      formData.repo?.id !== editingSpace.repo?.id
    )
    : true;

  const isFormEmpty = !formData.name?.trim() || !formData.space_code?.trim();

  const isCancelDisabled = isSaving;
  const isSaveDisabled = editingSpace
    ? !hasChanges || isSaving    
    : isFormEmpty || isSaving;     

  const inputClass = (hasError: boolean) =>
    `w-full h-11 rounded-lg border bg-muted/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition focus:ring-2 ${
      hasError
        ? 'border-destructive/70 focus:border-destructive focus:ring-destructive/15'
        : 'border-border/60 focus:border-foreground/40 focus:ring-foreground/8'
    }`;

  useEffect(() => {
    let isActive = true;
    const loadRepos = async () => {
      const repoData = await repoService.getAllRepos();
      if (isActive) setRepos(repoData);
    };
    loadRepos();
    return () => { isActive = false; };
  }, []);

  useEffect(() => {
    if (isOpen) {
      setErrors({});
      setIsSaving(false);
      setFormData(editingSpace ? { ...editingSpace } : { name: '', space_code: '' });
    }
  }, [isOpen, editingSpace]);

  const handleSave = async () => {
    setErrors({});

    const newErrors: Record<string, string> = {};
    if (!formData.name) newErrors.name = 'Space name is required';
    if (!formData.space_code) newErrors.space_code = 'Space code is required';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSaving(true);
    let success = false;

    try {
      if (editingSpace) {
        const nextSpace: ClickUpSpaceUpdateDTO = { ...editingSpace, ...formData };
        success = await onUpdate(nextSpace);
      } else {
        success = await onAdd({
          name: formData.name!,
          space_code: formData.space_code!,
        } as ClickUpSpaceCreateDTO);
      }
    } finally {
      setIsSaving(false);
    }

    if (success) {
      onClose();
    }
  };


  return (
    isOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
        <Card className="w-full max-w-[400px] border-border shadow-2xl">
            <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-foreground">
                {editingSpace ? 'Edit ClickUp Space' : 'Add New ClickUp Space'}
                </h2>
                <Button variant="ghost" size="icon" onClick={onClose} disabled={isCancelDisabled} className="h-8 w-8">
                <X className="w-4 h-4" />
                </Button>
            </div>

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
                    <div className="text-destructive text-xs mt-1 px-1">{errors.name}</div>
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
                    <div className="text-destructive text-xs mt-1 px-1">{errors.space_code}</div>
                )}
                </div>

                <div>
                <Label className="text-foreground font-medium">Linked Repository</Label>
                <Select
                    value={formData.repo?.id?.toString() || 'none'}
                    onValueChange={(repoId) => {
                    if (repoId === 'none') {
                        setFormData({ ...formData, repo: null });
                    } else {
                        const selectedRepo = repoOptions.find((r) => r.id?.toString() === repoId);
                        setFormData({
                        ...formData,
                        repo: selectedRepo
                            ? { id: selectedRepo.id ?? null, name: selectedRepo.name ?? null, url: selectedRepo.url ?? null }
                            : null,
                        });
                    }
                    }}
                    disabled={isSaving}
                >
                    <SelectTrigger className="mt-2 bg-input border-border text-foreground w-full">
                      <SelectValue placeholder="Select a repository..." />
                    </SelectTrigger>
                    <SelectContent className="bg-card border-border w-full">
                      {repoOptions.length === 0 ? (
                      <SelectItem value="none" disabled>
                        No repository available
                      </SelectItem>
                    ) : (
                      <>
                      <SelectItem value="none" className="text-muted-foreground hidden" disabled>
                        <span className="text-muted-foreground">No repository selected</span>
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
                    <p className="text-xs text-muted-foreground mt-2">
                    Selected: <span className="font-semibold">{formData.repo.name}</span>
                    </p>
                )}
                </div>
            </div>

            <div className="flex gap-2 pt-4 border-t border-border">
                <Button variant="outline" onClick={onClose} disabled={isCancelDisabled} className="flex-1">
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
                    Saving...
                    </>
                ) : (
                    <>
                    <CheckCircle2 className="w-4 h-4" />
                    {editingSpace ? 'Update' : 'Create'} Space
                    </>
                )}
                </Button>
            </div>
            </div>
        </Card>
        </div>
    )
  );
}