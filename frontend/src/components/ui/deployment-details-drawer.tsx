import { format } from 'date-fns';
import { X, ExternalLink, GitBranch, GitCommit, User, Clock, Server, Tag, FileText } from 'lucide-react';
import { Button } from '@/components/ui/shared-primitives/button';
import { Badge } from '@/components/ui/shared-primitives/badge';
import { Card } from '@/components/ui/shared-primitives/card';
import type { DeploymentDTO } from '@/api/api';
import { FieldRow } from './shared-primitives/field-row';

interface DeploymentDetailsDrawerProps {
  deployment: DeploymentDTO | null;
  onClose: () => void;
}

const STATUS_CONFIG: Record<string, { label: string; className: string }> = {
  success: { label: 'Success', className: 'bg-emerald-600 hover:bg-emerald-700' },
  failure: { label: 'Failed', className: 'bg-red-600 hover:bg-red-700' },
  error: { label: 'Error', className: 'bg-red-600 hover:bg-red-700' },
  pending: { label: 'Pending', className: 'bg-amber-600 hover:bg-amber-700' },
  waiting: { label: 'Waiting', className: 'bg-amber-600 hover:bg-amber-700' },
  queued: { label: 'Queued', className: 'bg-amber-600 hover:bg-amber-700' },
  in_progress: { label: 'In Progress', className: 'bg-amber-600 hover:bg-amber-700' },
  inactive: { label: 'Inactive', className: 'bg-slate-600 hover:bg-slate-700' },
  'no status': { label: 'No Status', className: 'bg-slate-500 hover:bg-slate-600' },
};

function getStatusBadge(state: string) {
  const config = STATUS_CONFIG[state] ?? { label: state, className: 'bg-slate-500 hover:bg-slate-600' };
  return <Badge className={`${config.className} text-white`}>{config.label}</Badge>;
}

export function DeploymentDetailsDrawer({ deployment, onClose }: DeploymentDetailsDrawerProps) {
  if (!deployment) return null;

  const hasLogUrl = deployment.log_url && deployment.log_url !== '-';
  const createdAt = deployment.created_at ? new Date(deployment.created_at) : null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4">
      <Card className="w-full sm:max-w-[480px] border-border shadow-2xl max-h-[90vh] flex flex-col">

        <div className="flex items-center justify-between px-4 sm:px-6 pt-4 sm:pt-6 shrink-0">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-muted-foreground" />
            <h2 className="text-lg sm:text-xl font-bold text-foreground">Deployment Details</h2>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 shrink-0">
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="flex items-center justify-between gap-3 px-4 sm:px-6 py-3 mx-4 sm:mx-6 mt-4 rounded-lg bg-muted/40 border border-border/60 shrink-0">
          <div>
            <p className="text-xs text-muted-foreground mb-0.5">Environment</p>
            <p className="text-base font-bold text-foreground">{deployment.environment || 'N/A'}</p>
          </div>
          {getStatusBadge(deployment.state || 'unknown')}
        </div>

        <div className="space-y-0 px-4 sm:px-6 py-4 overflow-y-auto flex-1">
          <FieldRow
            icon={<Tag className="w-4 h-4" />}
            label="Deployment ID"
            value={`#${deployment.dep_id}`}
          />
          <FieldRow
            icon={<GitBranch className="w-4 h-4" />}
            label="Branch / Ref"
            value={deployment.ref || 'N/A'}
          />
          <FieldRow
            icon={<GitCommit className="w-4 h-4" />}
            label="Commit SHA"
            value={
              <span className="font-mono bg-muted px-2 py-0.5 rounded text-xs">
                {deployment.sha || 'N/A'}
              </span>
            }
          />
          <FieldRow
            icon={<User className="w-4 h-4" />}
            label="Created By"
            value={deployment.creator || 'Unknown'}
          />
          <FieldRow
            icon={<Clock className="w-4 h-4" />}
            label="Created At"
            value={createdAt ? format(createdAt, "PPP 'at' HH:mm:ss") : 'N/A'}
          />
          <FieldRow
            icon={<FileText className="w-4 h-4" />}
            label="Description"
            value={deployment.description || '—'}
          />
          <FieldRow
            icon={<ExternalLink className="w-4 h-4" />}
            label="Log URL"
            value={
              hasLogUrl ? (
                <a
                  href={deployment.log_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary underline underline-offset-2 hover:text-primary/80 transition-colors break-all"
                >
                  {deployment.log_url}
                </a>
              ) : (
                <span className="text-muted-foreground italic">No logs available</span>
              )
            }
          />
        </div>

        <div className="flex gap-2 px-4 sm:px-6 pb-4 sm:pb-6 pt-4 border-t border-border shrink-0">
          {hasLogUrl && (
            <Button asChild className="flex-1 gap-2">
              <a href={deployment.log_url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4" />
                Open Logs
              </a>
            </Button>
          )}
          <Button
            variant="outline"
            className={hasLogUrl ? 'flex-1' : 'w-full'}
            onClick={onClose}
          >
            Close
          </Button>
        </div>

      </Card>
    </div>
  );
}