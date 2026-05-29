import { useState } from 'react';
import type { 
  AssociateClickUpSpaceRequest, 
  ClickUpSpaceLightDTO, 
  GitRepoCreateDTO, 
  GitRepoDetailDTO, 
  GitRepoUpdateDTO, 
  MemberDTO 
} from '@/api/api';
import { Button } from '@/components/ui/shared-primitives/button';
import { 
  Edit2, 
  Trash2, 
  Plus, 
  GitBranch, 
  Users, 
  Link as LinkIcon, 
  AlertCircle
} from 'lucide-react';
import { Badge } from '@/components/ui/shared-primitives/badge';
import { Avatar, AvatarFallback } from '@/components/ui/shared-primitives/avatar';
import { RepoEditModalNew } from './ui/repo-edit-modal-new';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/shared-primitives/dialog';

interface ReposTableProps {
  repos: GitRepoDetailDTO[];
  clickUpSpaces: ClickUpSpaceLightDTO[];
  availableMembers: MemberDTO[];
  onUpdate: (repo: GitRepoUpdateDTO) => Promise<boolean>;
  onDelete: (id: number) => void;
  onAdd: (repo: GitRepoCreateDTO) => Promise<boolean>;
  isLoading?: boolean;
  onAssociate: (association: AssociateClickUpSpaceRequest) => Promise<boolean>;
  refreshSpaces?: () => void;
  error?: string | null;
  refreshRepos?: () => void;
}

export function ReposTable({ 
  repos, 
  clickUpSpaces, 
  availableMembers, 
  onUpdate, 
  onDelete, 
  onAdd, 
  isLoading, 
  onAssociate, 
  refreshSpaces, 
  error,
  refreshRepos 
}: ReposTableProps) {
  const [selectedRepo, setSelectedRepo] = useState<GitRepoDetailDTO | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [deleteConfirmRepoId, setDeleteConfirmRepoId] = useState<number | null>(null);

  const handleEditClick = (repo: GitRepoDetailDTO) => {
    setSelectedRepo(repo);
    setIsEditModalOpen(true);
  };

  const handleAddClick = () => {
    setSelectedRepo(null);
    setIsAddModalOpen(true);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap justify-between gap-2">
        <h2 className="text-xl sm:text-2xl font-bold text-foreground">GitHub Repositories</h2>
        <Button onClick={handleAddClick} className="gap-2 shrink-0">
          <Plus className="w-4 h-4" />
          Add Repository
        </Button>
      </div>

      <div className="hidden sm:block overflow-x-auto overflow-y-auto max-h-[480px] border border-border rounded-lg">
        {isLoading ? (
          <table className="w-full min-w-[600px]">
            <tbody>
              {Array.from({ length: 4 }).map((_, i) => (
                <tr key={i} className="border-b border-border">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3 justify-center">
                      <div className="w-5 h-5 rounded bg-muted animate-pulse" />
                      <div className="h-4 w-32 rounded bg-muted animate-pulse" />
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-48 rounded bg-muted animate-pulse mx-auto" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-1 justify-center">
                      {Array.from({ length: 3 }).map((_, j) => (
                        <div key={j} className="w-8 h-8 rounded-full bg-muted animate-pulse" />
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-6 w-24 rounded-full bg-muted animate-pulse mx-auto" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end gap-2">
                      <div className="w-8 h-8 rounded bg-muted animate-pulse" />
                      <div className="w-8 h-8 rounded bg-muted animate-pulse" />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : error ? (
          <table className="w-full min-w-[600px]">
            <tbody>
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <div className="flex items-center gap-2 text-destructive text-sm">
                      <AlertCircle className="w-4 h-4" />
                      Failed to load repositories.
                    </div>
                    <button
                      onClick={() => refreshRepos?.()}
                      className="text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground transition"
                    >
                      Try again
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        ) : (
          <table className="w-full min-w-[600px]">
            <thead className="sticky top-0 z-10">
              <tr className="border-b border-border bg-muted">
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">
                  Repository
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">
                  URL
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">
                  Members
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-foreground">
                  ClickUp Space
                </th>
                <th className="px-12 py-4 text-right text-sm font-semibold text-foreground">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {repos.length > 0 ? (
                repos.map((repo) => (
                  <tr
                    key={repo.id ?? repo.url ?? repo.name}
                    className="border-b border-border hover:bg-muted/50 transition-colors"
                  >
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center gap-3 justify-center">
                        <GitBranch className="w-5 h-5 text-primary" />
                        <span className="font-medium text-foreground">{repo.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      {repo.url ? (
                        <a
                          href={repo.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline flex items-center gap-1 w-full justify-center"
                        >
                          <LinkIcon className="w-4 h-4 shrink-0" />
                          <span className="text-sm truncate max-w-[140px] lg:max-w-xs">
                            <span className="truncate">{repo.url.replace('https://github.com/', '')}</span>
                          </span>
                        </a>
                      ) : (
                        <span className="text-sm text-muted-foreground">No URL</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center gap-2 justify-center">
                        <div className="flex -space-x-2">
                          {(repo.members ?? []).slice(0, 3).map((member) => (
                            <Avatar key={member.id ?? member.username} className="w-8 h-8 border border-background">
                              <AvatarFallback className="text-xs bg-primary text-primary-foreground">
                                {(member.username || 'M')[0].toUpperCase()}
                              </AvatarFallback>
                            </Avatar>
                          ))}
                          {(repo.members?.length ?? 0) > 3 && (
                            <div className="w-8 h-8 flex items-center justify-center bg-muted rounded-full border border-background text-xs font-semibold text-foreground">
                              +{(repo.members?.length ?? 0) - 3}
                            </div>
                          )}
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="gap-1"
                          onClick={() => handleEditClick(repo)}
                        >
                          <Users className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      {repo.clickup_space ? (
                        <Badge
                          variant="secondary"
                          className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                        >
                          {repo.clickup_space.name}
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-muted-foreground">
                          Not assigned
                        </Badge>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditClick(repo)}
                          className="text-primary hover:bg-primary/10"
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            if (typeof repo.id === 'number') {
                              setDeleteConfirmRepoId(repo.id);
                            }
                          }}
                          className="text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <p className="text-muted-foreground">No repositories yet. Create your first repository!</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      <div className="sm:hidden space-y-3 max-h-[60vh] overflow-y-auto overflow-x-auto pr-1 max-w-full">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-lg border border-border p-4 space-y-2 animate-pulse">
              <div className="h-4 w-32 bg-muted rounded" />
              <div className="h-3 w-48 bg-muted rounded" />
              <div className="h-3 w-24 bg-muted rounded" />
            </div>
          ))
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <div className="flex items-center gap-2 text-destructive text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              Failed to load repositories.
            </div>
            <button
              onClick={() => refreshRepos?.()}
              className="text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground transition"
            >
              Try again
            </button>
          </div>
        ) : repos.length > 0 ? (
          repos.map((repo) => (
            <div key={repo.id ?? repo.url} className="rounded-lg border border-border p-4 bg-card space-y-2">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <GitBranch className="w-4 h-4 text-primary" />
                  <span className="font-medium text-foreground truncate">{repo.name}</span>
                </div>
                <div className="flex gap-1 shrink-0">
                  <Button variant="ghost" size="icon" onClick={() => handleEditClick(repo)} className="h-8 w-8 text-primary">
                    <Edit2 className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost" size="icon"
                    onClick={() => typeof repo.id === 'number' && setDeleteConfirmRepoId(repo.id)}
                    className="h-8 w-8 text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {repo.url && (
                <a href={repo.url} target="_blank" rel="noopener noreferrer"
                  className="text-primary text-xs flex items-center gap-1 hover:underline">
                  <LinkIcon className="w-3 h-3 shrink-0" />
                  <span className="truncate">{repo.url.replace('https://github.com/', '')}</span>
                </a>
              )}

              <div className="flex items-center justify-between">
                <div className="flex -space-x-2">
                  {(repo.members ?? []).slice(0, 3).map((member) => (
                    <Avatar key={member.id ?? member.username} className="w-7 h-7 border border-background">
                      <AvatarFallback className="text-xs bg-primary text-primary-foreground">
                        {(member.username || 'M')[0].toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  ))}
                  {(repo.members?.length ?? 0) > 3 && (
                    <div className="w-7 h-7 flex items-center justify-center bg-muted rounded-full border border-background text-xs font-semibold">
                      +{(repo.members?.length ?? 0) - 3}
                    </div>
                  )}
                </div>

                {repo.clickup_space ? (
                  <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {repo.clickup_space.name}
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-muted-foreground">Not assigned</Badge>
                )}
              </div>
            </div>
          ))
        ) : (
          <p className="text-center text-muted-foreground py-8">No repositories yet. Create your first repository!</p>
        )}
      </div>

      <RepoEditModalNew
        repo={selectedRepo}
        isOpen={isEditModalOpen || isAddModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setIsAddModalOpen(false);
          setSelectedRepo(null);
        }}
        onSave={onAdd}
        onUpdate={onUpdate}
        clickUpSpaces={clickUpSpaces}
        availableMembers={availableMembers}
        onAssociate={onAssociate}
        refreshSpaces={refreshSpaces}
      />

      <Dialog open={deleteConfirmRepoId !== null} onOpenChange={(open) => { if (!open) setDeleteConfirmRepoId(null); }}>
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>Are you sure you want to delete?</DialogTitle>
            <DialogDescription>
              This action cannot be undone. The repository will be permanently deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex flex-col-reverse sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setDeleteConfirmRepoId(null)}>
              No
            </Button>
            <Button
              variant="destructive"
              onClick={async () => {
                if (deleteConfirmRepoId !== null) {
                  const repo = repos.find((r) => r.id === deleteConfirmRepoId);
                  await onDelete(deleteConfirmRepoId);
                  setDeleteConfirmRepoId(null);
                  if (repo && repo.clickup_space) {
                    refreshSpaces?.();
                  }
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