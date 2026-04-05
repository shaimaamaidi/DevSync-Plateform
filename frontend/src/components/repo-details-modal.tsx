import type { GitRepoDetailDTO } from '@/api/api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { MembersList } from './members-list';
import { ExternalLink, Tag, GitBranch } from 'lucide-react';

interface RepoDetailsModalProps {
  repo: GitRepoDetailDTO | null;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function RepoDetailsModal({
  repo,
  isOpen,
  onOpenChange,
}: RepoDetailsModalProps) {
  if (!repo) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GitBranch className="w-6 h-6 text-primary" />
            {repo.name}
          </DialogTitle>
          <DialogDescription>{repo.url}</DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          <div className="border border-border rounded-lg p-4 space-y-4">
            <h3 className="font-semibold text-foreground">Repository Information</h3>

            <div className="space-y-3">
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
                  Repository URL
                </p>
                {repo.url ? (
                  <a
                    href={repo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline flex items-center gap-2 w-fit"
                  >
                    {repo.url}
                    <ExternalLink className="w-4 h-4" />
                  </a>
                ) : (
                  <span className="text-muted-foreground">No repository URL</span>
                )}
              </div>

              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
                  Repository ID
                </p>
                <p className="font-mono text-sm text-foreground">{repo.id}</p>
              </div>
            </div>
          </div>

          <div className="border border-border rounded-lg p-4 space-y-4">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <Tag className="w-5 h-5 text-primary" />
              ClickUp Space Assignment
            </h3>

            {repo.clickup_space ? (
              <div className="flex items-center gap-3">
                <div>
                  <p className="font-medium text-foreground">{repo.clickup_space?.name}</p>
                  <p className="text-xs text-muted-foreground">Assigned</p>
                </div>
              </div>
            ) : (
              <div className="text-muted-foreground text-sm py-4 text-center">
                <p>No ClickUp space assigned</p>
              </div>
            )}
          </div>

          <div className="border border-border rounded-lg p-4">
            <MembersList members={repo.members ?? []} />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
