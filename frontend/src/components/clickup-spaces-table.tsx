import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import type { 
  ClickUpSpaceLightDTO, 
  ClickUpSpaceUpdateDTO, 
  CreateSpaceRequest, 
  ClickUpSpaceRegisterDTO, 
  GitRepoDetailDTO, 
  AssociateClickUpSpaceRequest 
} from '@/api/api';
import { Button } from '@/components/ui/button';
import { Plus, Edit2, Trash2, Eye, Link as LinkIcon } from 'lucide-react';
import { ClickUpEditModal } from './ui/clickup-edit-model-new';
import { useNavigate } from 'react-router-dom';

export interface ClickUpSpacesTableProps {
  spaces: ClickUpSpaceLightDTO[];
  onUpdate: (space: ClickUpSpaceUpdateDTO) => Promise<boolean>;
  onDelete: (id: number) => Promise<boolean>;
  onRemove: (spaceCode: number) => Promise<boolean>; 
  onCreate: (space: CreateSpaceRequest) => Promise<boolean>;
  onRegister: (space: ClickUpSpaceRegisterDTO) => Promise<boolean | undefined>;
  isLoading?: boolean;
  showNotFoundDialog?: boolean;
  onNotFoundDialogChange?: (show: boolean) => void;
  showNameMismatchDialog?: boolean;
  onNameMismatchDialogChange?: (show: boolean) => void;
  repositories: GitRepoDetailDTO[];
  onAssociate: (association: AssociateClickUpSpaceRequest) => Promise<boolean>;
  refreshSpaces?: () => void;
}

export function ClickUpSpacesTable({ 
  spaces, 
  onUpdate, 
  onDelete, 
  onRemove,
  onCreate, 
  onRegister, 
  isLoading ,
  showNotFoundDialog,
  onNotFoundDialogChange,
  showNameMismatchDialog,
  onNameMismatchDialogChange,
  repositories,
  onAssociate,
  refreshSpaces,
}: ClickUpSpacesTableProps) {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSpace, setEditingSpace] = useState<ClickUpSpaceLightDTO | null>(null);
  const [deleteConfirmSpaceId, setDeleteConfirmSpaceId] = useState<number | null>(null);
  const [showDeleteModeDialog, setShowDeleteModeDialog] = useState(false);

  const handleAddClick = () => {
    setEditingSpace(null);
    setIsModalOpen(true);
  };

  const handleEditClick = (space: ClickUpSpaceLightDTO) => {
    setEditingSpace(space);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setEditingSpace(null);
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

      <div className="hidden sm:block overflow-x-auto border border-border rounded-lg">
        {isLoading ? (
          <table className="w-full">
            <tbody>
              {Array.from({ length: 4 }).map((_, i) => (
                <tr key={i} className="border-b border-border">
                  <td className="px-6 py-4">
                    <div className="h-4 w-32 rounded bg-muted animate-pulse mx-auto" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-48 rounded bg-muted animate-pulse mx-auto" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-48 rounded bg-muted animate-pulse mx-auto" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end gap-2">
                      <div className="w-8 h-8 rounded bg-muted animate-pulse" />
                      <div className="w-8 h-8 rounded bg-muted animate-pulse" />
                      <div className="w-8 h-8 rounded bg-muted animate-pulse" />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted">
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Space Name</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Space ID</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">Linked Repository</th>
                <th className="px-6 py-4 pr-14 text-right text-sm font-semibold text-foreground">Actions</th>
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
                      <span className="font-medium text-foreground w-full text-center block">{space.name}</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="font-mono text-sm text-muted-foreground">{space.space_code || 'N/A'}</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      {space.repo?.url ? (
                        <a
                          href={space.repo.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline flex items-center gap-1 w-full justify-center"
                        >
                          <LinkIcon className="w-4 h-4" />
                          <span className="text-sm truncate max-w-xs">
                            {space.repo.url.replace('https://github.com/', '')}
                          </span>
                          {space.repo.name && (
                            <span className="ml-1 text-xs text-muted-foreground">({space.repo.name})</span>
                          )}
                        </a>
                      ) : space.repo?.name ? (
                        <span className="text-sm text-foreground flex items-center gap-1 justify-center w-full">
                          <LinkIcon className="w-4 h-4 opacity-60" />
                          {space.repo.name}
                        </span>
                      ) : (
                        <span className="text-sm text-muted-foreground italic">No repo linked</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => space.space_code ? navigate(`/spaces/${space.space_code}/tasks`) : null}
                          className="h-8 w-8"
                          disabled={!space.space_code}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
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
        )}
      </div>

      <div className="sm:hidden space-y-3">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-lg border border-border p-4 space-y-2 animate-pulse">
              <div className="h-4 w-32 bg-muted rounded" />
              <div className="h-3 w-24 bg-muted rounded" />
              <div className="h-3 w-40 bg-muted rounded" />
            </div>
          ))
        ) : spaces.length > 0 ? (
          spaces.map((space, index) => (
            <div key={space.id ?? index} className="rounded-lg border border-border p-4 space-y-2 bg-card">
              <div className="flex items-center justify-between">
                <span className="font-medium text-foreground">{space.name}</span>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => space.space_code ? navigate(`/spaces/${space.space_code}/tasks`) : null} className="h-8 w-8" disabled={!space.space_code}>
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => handleEditClick(space)} className="h-8 w-8">
                    <Edit2 className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => typeof space.id === 'number' && setDeleteConfirmSpaceId(space.id)}
                    className="h-8 w-8 text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <p className="text-xs font-mono text-muted-foreground">{space.space_code || 'N/A'}</p>
              {space.repo?.url ? (
                <a href={space.repo.url} target="_blank" rel="noopener noreferrer"
                  className="text-primary text-xs flex items-center gap-1 hover:underline">
                  <LinkIcon className="w-3 h-3" />
                  {space.repo.url.replace('https://github.com/', '')}
                </a>
              ) : (
                <span className="text-xs text-muted-foreground italic">No repo linked</span>
              )}
            </div>
          ))
        ) : (
          <p className="text-center text-muted-foreground py-8">No spaces yet. Create your first space!</p>
        )}
      </div>

      <ClickUpEditModal
        isOpen={isModalOpen}
        repositories={repositories}
        editingSpace={editingSpace}
        onClose={handleModalClose}
        onCreate={onCreate}
        onRegister={onRegister}
        onUpdate={onUpdate}
        showNotFoundDialog={showNotFoundDialog}
        onNotFoundDialogChange={onNotFoundDialogChange}
        showNameMismatchDialog={showNameMismatchDialog}
        onNameMismatchDialogChange={onNameMismatchDialogChange}
        onAssociate={onAssociate}
        refreshSpaces={refreshSpaces}
      />

      <Dialog
        open={deleteConfirmSpaceId !== null}
        onOpenChange={(open) => { if (!open) setDeleteConfirmSpaceId(null); }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Are you sure you want to delete this ClickUp space?</DialogTitle>
            <DialogDescription>
              This action cannot be undone. The ClickUp space will be permanently deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmSpaceId(null)}>No</Button>
            <Button
              variant="destructive"
              onClick={() => {
                setShowDeleteModeDialog(true);
              }}
            >
              Yes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog
        open={showDeleteModeDialog}
        onOpenChange={(open) => {
          if (!open) {
            setShowDeleteModeDialog(false);
            setDeleteConfirmSpaceId(null);
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Choose deletion mode</DialogTitle>
            <DialogDescription>
              How would you like to delete this space?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex flex-col sm:flex-row gap-2">
            <Button
              variant="outline"
              onClick={async () => {
                if (deleteConfirmSpaceId !== null) {
                  const result = await onDelete(deleteConfirmSpaceId);
                  setShowDeleteModeDialog(false);
                  setDeleteConfirmSpaceId(null);
                  if (result) 
                    refreshSpaces?.();
                }
              }}
            >
              Remove from DB only
            </Button>
            <Button
              variant="destructive"
              onClick={async () => {
                if (deleteConfirmSpaceId !== null) {
                  const result = await onRemove(deleteConfirmSpaceId);
                  setShowDeleteModeDialog(false);
                  setDeleteConfirmSpaceId(null);
                  if (result) 
                    refreshSpaces?.();
                }
              }}
            >
              Remove from DB + ClickUp
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}