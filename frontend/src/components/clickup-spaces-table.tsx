import { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import type { ClickUpSpaceLightDTO, GitRepoDTO } from '@/api/api';
import { repoService } from '@/services/repo-service';
import { Button } from '@/components/ui/button';
import { Plus, Edit2, Trash2, X } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export interface ClickUpSpacesTableProps {
  spaces: ClickUpSpaceLightDTO[];
  onUpdate: (space: ClickUpSpaceLightDTO) => void;
  onDelete: (id: number) => void;
  onAdd: (space: ClickUpSpaceLightDTO) => void;
}

export function ClickUpSpacesTable({ spaces, onUpdate, onDelete, onAdd }: ClickUpSpacesTableProps) {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingSpace, setEditingSpace] = useState<ClickUpSpaceLightDTO | null>(null);
  const [formData, setFormData] = useState<Partial<ClickUpSpaceLightDTO>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [deleteConfirmSpaceId, setDeleteConfirmSpaceId] = useState<number | null>(null);

  // Reset errors when modal is opened or closed
  useEffect(() => {
    if (!isAddModalOpen) {
      setErrors({});
    }
  }, [isAddModalOpen]);
  const [repos, setRepos] = useState<GitRepoDTO[]>([]);
  const repoOptions = repos.filter(
    (repo): repo is GitRepoDTO & { id: number } => typeof repo.id === 'number'
  );

  useEffect(() => {
    let isActive = true;

    const loadRepos = async () => {
      const repoData = await repoService.getAllRepos();
      if (isActive) {
        setRepos(repoData);
      }
    };

    loadRepos();

    return () => {
      isActive = false;
    };
  }, []);

  const handleAddClick = () => {
    setEditingSpace(null);
    setIsAddModalOpen(true);
  };

  // Reset formData when opening add modal
  useEffect(() => {
    if (isAddModalOpen && editingSpace === null) {
      setFormData({ name: '', space_code: '' });
    }
  }, [isAddModalOpen, editingSpace]);

  const handleEditClick = (space: ClickUpSpaceLightDTO) => {
    setEditingSpace(space);
    setFormData(space);
    setIsAddModalOpen(true);
  };

  const handleSave = () => {
    setErrors({});
    if (!formData.name || !formData.space_code) {
      const newErrors: Record<string, string> = {};
      if (!formData.name) newErrors.name = 'Space name is required';
      if (!formData.space_code) newErrors.space_code = 'Space code is required';
      setErrors(newErrors);
      return;
    }

    const baseSpace = editingSpace ?? {};
    const nextSpace: ClickUpSpaceLightDTO = {
      ...baseSpace,
      ...formData,
    };

    if (editingSpace) {
      onUpdate(nextSpace);
    } else {
      onAdd(nextSpace);
    }

    setIsAddModalOpen(false);
    setFormData({});
    setErrors({});
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">ClickUp Spaces</h2>
        <Button onClick={handleAddClick} className="gap-2">
          <Plus className="w-4 h-4" />
          Add Space
        </Button>
      </div>
      <div className="overflow-x-auto border border-border rounded-lg">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted">
              <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                Space Name
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                Space ID
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                Linked Repository
              </th>
              <th className="px-6 py-4 text-right text-sm font-semibold text-foreground">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {spaces.length > 0 ? (
              spaces.map((space, index) => (
                <tr
                  key={space.id ?? space.space_code ?? space.name ?? index}
                  className="border-b border-border hover:bg-muted/50 transition-colors"
                >
                  <td className="px-6 py-4">
                    <span className="font-medium text-foreground">{space.name}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm text-muted-foreground">{space.space_code || 'N/A'}</span>
                  </td>
                  <td className="px-6 py-4">
                    {space.repo?.name ? (
                      <span className="text-sm text-foreground">{space.repo.name}</span>
                    ) : (
                      <span className="text-sm text-muted-foreground italic">No repo linked</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEditClick(space)}
                        className="h-8 w-8"
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          if (typeof space.id === 'number') {
                            setDeleteConfirmSpaceId(space.id);
                          }
                        }}
                        className="h-8 w-8 text-destructive hover:bg-destructive/10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center">
                  <p className="text-muted-foreground">No spaces yet. Create your first space!</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add/Edit Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-md border-border shadow-2xl">
            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-foreground">
                  {editingSpace ? 'Edit Space' : 'Add New Space'}
                </h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsAddModalOpen(false)}
                  className="h-8 w-8"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>

              <div className="space-y-4">

                <div>
                  <Label className="text-foreground font-medium">Space Name</Label>
                  <Input
                    type="text"
                    placeholder="My ClickUp Space"
                    value={formData.name || ''}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="mt-2 bg-input border-border text-foreground"
                  />
                  {errors.name && (
                    <div className="text-red-500 text-xs mt-1">{errors.name}</div>
                  )}
                </div>

                <div>
                  <Label className="text-foreground font-medium">Space ID</Label>
                  <Input
                    type="text"
                    placeholder="cus_prod_001"
                    value={formData.space_code || ''}
                    onChange={(e) => setFormData({ ...formData, space_code: e.target.value })}
                    className="mt-2 bg-input border-border text-foreground"
                  />
                  {errors.space_code && (
                    <div className="text-red-500 text-xs mt-1">{errors.space_code}</div>
                  )}
                </div>

                <div>
                  <Label className="text-foreground font-medium">Linked Repository</Label>
                  <Select value={formData.repo?.id?.toString() || 'none'} onValueChange={(repoId) => {
                    if (repoId === 'none') {
                      setFormData({ ...formData, repo: null });
                    } else {
                      const selectedRepo = repoOptions.find((repo) => repo.id?.toString() === repoId);
                      setFormData({
                        ...formData,
                        repo: selectedRepo
                          ? { id: selectedRepo.id ?? null, name: selectedRepo.name ?? null, url: selectedRepo.url ?? null }
                          : null,
                      });
                    }
                  }}>
                    <SelectTrigger className="mt-2 bg-input border-border text-foreground">
                      <SelectValue placeholder="Select a repository..." />
                    </SelectTrigger>
                    <SelectContent className="bg-card border-border">
                      <SelectItem value="none">No repository</SelectItem>
                      {repoOptions.map((repo, repoIndex) => (
                        <SelectItem
                          key={repo.id ?? repo.url ?? repoIndex}
                          value={repo.id.toString()}
                        >
                          {repo.url ?? 'Unknown repo'} ({repo.name ?? 'Unnamed'})
                        </SelectItem>
                      ))}
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
                <Button
                  variant="outline"
                  onClick={() => setIsAddModalOpen(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button onClick={handleSave} className="flex-1">
                  {editingSpace ? 'Update' : 'Add'} Space
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmSpaceId !== null} onOpenChange={(open) => { if (!open) setDeleteConfirmSpaceId(null); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Are you sure you want to delete this ClickUp space?</DialogTitle>
            <DialogDescription>
              This action cannot be undone. The ClickUp space will be permanently deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmSpaceId(null)}>
              No
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (deleteConfirmSpaceId !== null) {
                  onDelete(deleteConfirmSpaceId);
                  setDeleteConfirmSpaceId(null);
                }
              }}
            >
              Yes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

