import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/shared-primitives/card';
import { Badge } from '@/components/ui/shared-primitives/badge';
import { Button } from '@/components/ui/shared-primitives/button';
import { ChevronLeft, ChevronRight, ExternalLink, Filter, X, Eye } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { DeploymentDTO } from '@/api/api';
import type { DeploymentStatus } from '@/types/deployment';
import { DeploymentDetailsDrawer } from './deployment-details-drawer';
import { createPortal } from 'react-dom';

const PER_PAGE = 5;

interface DeploymentsListProps {
  deployments: DeploymentDTO[];
}

const resolveStatus = (state: string): 'success' | 'failure' | 'pending' | 'inactive' | 'unknown' => {
  switch (state) {
    case 'success':
      return 'success';
    case 'failure':
    case 'error':
      return 'failure';
    case 'pending':
    case 'waiting':
    case 'queued':
    case 'in_progress':
      return 'pending';
    case 'inactive':
      return 'inactive';
    default:
      return 'unknown';
  }
};

export function DeploymentsList({ deployments }: DeploymentsListProps) {
  const [statusFilter, setStatusFilter] = useState<DeploymentStatus>('all');
  const [selectedDeployment, setSelectedDeployment] = useState<DeploymentDTO | null>(null);
  const [page, setPage] = useState(1);

  const getStatus = (deployment: DeploymentDTO) => deployment.state ?? 'unknown';

  const filteredDeployments =
    statusFilter === 'all'
      ? deployments
      : deployments.filter((d) => resolveStatus(getStatus(d)) === statusFilter);

  useEffect(() => {
    setPage(1);
  }, [statusFilter]);

  const paginatedDeployments = filteredDeployments.slice(
    (page - 1) * PER_PAGE,
    page * PER_PAGE
  );

  const hasNext = page * PER_PAGE < filteredDeployments.length;
  const hasPrev = page > 1;

  const getStatusColor = (state: string) => {
    switch (resolveStatus(state)) {
      case 'success': return 'bg-emerald-500/10 border-emerald-500/20';
      case 'failure': return 'bg-red-500/10 border-red-500/20';
      case 'pending': return 'bg-amber-500/10 border-amber-500/20';
      case 'inactive': return 'bg-slate-500/10 border-slate-500/20';
      default: return 'bg-slate-500/10 border-slate-500/20';
    }
  };

  const getStatusBadge = (state: string) => {
    switch (resolveStatus(state)) {
      case 'success':
        return (
          <Badge className="gap-1 !bg-emerald-600 hover:bg-emerald-700">
            <span className="w-2 h-2 bg-emerald-300 rounded-full animate-pulse" />
            Success
          </Badge>
        );
      case 'failure':
        return (
          <Badge className="gap-1 !bg-red-600 hover:bg-red-700">
            <span className="w-2 h-2 bg-red-300 rounded-full" />
            {state === 'error' ? 'Error' : 'Failed'}
          </Badge>
        );
      case 'pending':
        return (
          <Badge className="gap-1 !bg-amber-600 hover:bg-amber-700">
            <span className="w-2 h-2 bg-amber-300 rounded-full animate-pulse" />
            {state === 'in_progress' ? 'In Progress' : state === 'waiting' ? 'Waiting' : 'Pending'}
          </Badge>
        );
      case 'inactive':
        return (
          <Badge className="gap-1 bg-slate-600 hover:bg-slate-700">
            <span className="w-2 h-2 bg-slate-300 rounded-full" />
            Inactive
          </Badge>
        );
      default:
        return (
          <Badge variant="secondary" className="gap-1">
            <span className="w-2 h-2 bg-muted-foreground/40 rounded-full" />
            {state === 'no status' ? 'No Status' : state}
          </Badge>
        );
    }
  };

  return (
    <>
      <div className="space-y-6">
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Status:</span>
          <div className="flex gap-2 flex-wrap">
            {(['all', 'success', 'pending', 'failure', 'inactive'] as const).map((status) => (
              <Button
                key={status}
                variant={statusFilter === status ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter(status as DeploymentStatus)}
                className="capitalize"
              >
                {status}
              </Button>
            ))}
          </div>
          {statusFilter !== 'all' && (
            <Button variant="ghost" size="sm" onClick={() => setStatusFilter('all')} className="gap-1">
              <X className="w-3 h-3" />
              Clear
            </Button>
          )}
        </div>

        <div className="space-y-3">
          <div className="hidden sm:grid grid-cols-6 gap-3 text-xs font-semibold text-foreground text-center px-4">
            <div>Environment</div>
            <div>Branch</div>
            <div>Commit</div>
            <div>Author</div>
            <div>Deployed</div>
            <div>Actions</div>
          </div>

          <div className="space-y-3">
            {paginatedDeployments.length > 0 ? (
              paginatedDeployments.map((deployment, index) => {
                const state = getStatus(deployment);
                const createdAt = deployment.created_at ? new Date(deployment.created_at) : null;
                const hasLogUrl = deployment.log_url && deployment.log_url !== '-';

                return (
                  <Card
                    key={deployment.dep_id ?? `${deployment.environment ?? 'deployment'}-${index}`}
                    className={`px-4 py-3 border ${getStatusColor(state)} transition-all hover:shadow-md`}
                  >
                    <div className="grid grid-cols-2 sm:grid-cols-6 gap-3 text-xs text-center items-center">
                      <div className="flex flex-col items-center gap-1 col-span-2 sm:col-span-1">
                        <span className="text-sm font-semibold text-foreground truncate max-w-full">
                          {deployment.environment || 'N/A'}
                        </span>
                        {getStatusBadge(state)}
                      </div>

                      <div>
                        <p className="text-muted-foreground sm:hidden text-[10px] mb-0.5">Branch</p>
                        <p className="font-medium text-foreground">{deployment.ref || 'N/A'}</p>
                      </div>

                      <div>
                        <p className="text-muted-foreground sm:hidden text-[10px] mb-0.5">Commit</p>
                        <p className="font-mono text-foreground">
                          {deployment.sha ? deployment.sha.slice(0, 7) : 'N/A'}
                        </p>
                      </div>

                      <div>
                        <p className="text-muted-foreground sm:hidden text-[10px] mb-0.5">Author</p>
                        <p className="font-medium text-foreground">{deployment.creator || 'Unknown'}</p>
                      </div>

                      <div>
                        <p className="text-muted-foreground sm:hidden text-[10px] mb-0.5">Deployed</p>
                        <p className="font-medium text-foreground">
                          {createdAt ? formatDistanceToNow(createdAt, { addSuffix: true }) : 'N/A'}
                        </p>
                      </div>

                      <div className="flex items-center justify-center gap-1">
                        {hasLogUrl ? (
                          <a
                            href={deployment.log_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1 hover:bg-background rounded-lg transition-colors flex-shrink-0"
                            title="Open logs"
                          >
                            <ExternalLink className="w-4 h-4 text-primary" />
                          </a>
                        ) : (
                          <span
                            className="p-1 rounded-lg flex-shrink-0 cursor-not-allowed opacity-30"
                            title="No logs available"
                          >
                            <ExternalLink className="w-4 h-4 text-muted-foreground" />
                          </span>
                        )}

                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0"
                          title="View details"
                          onClick={() => setSelectedDeployment(deployment)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                );
              })
            ) : (
              <Card className="p-8 text-center border-dashed">
                <p className="text-muted-foreground">
                  {statusFilter === 'all' ? 'No deployments available' : `No ${statusFilter} deployments found`}
                </p>
              </Card>
            )}
          </div>

          {filteredDeployments.length > PER_PAGE && (
            <div className="flex items-center justify-between pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => p - 1)}
                disabled={!hasPrev}
                className="gap-1"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {page} of {Math.ceil(filteredDeployments.length / PER_PAGE)}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={!hasNext}
                className="gap-1"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>

        {deployments.length > 0 && (
          <Card className="p-4 bg-muted/50 border-border">
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-emerald-600">
                  {deployments.filter((d) => resolveStatus(getStatus(d)) === 'success').length}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Successful</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-amber-600">
                  {deployments.filter((d) => resolveStatus(getStatus(d)) === 'pending').length}
                </p>
                <p className="text-xs text-muted-foreground mt-1">In Progress</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-red-600">
                  {deployments.filter((d) => resolveStatus(getStatus(d)) === 'failure').length}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Failed</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-500">
                  {deployments.filter((d) => resolveStatus(getStatus(d)) === 'inactive').length}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Inactive</p>
              </div>
            </div>
          </Card>
        )}
      </div>
      
      {selectedDeployment && createPortal(
        <DeploymentDetailsDrawer
          deployment={selectedDeployment}
          onClose={() => setSelectedDeployment(null)}
        />,
        document.body
      )}
    </>
  );
}