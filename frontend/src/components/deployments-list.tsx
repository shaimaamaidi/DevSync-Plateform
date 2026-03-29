import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, Filter, X } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { DeploymentDTO } from '@/api/api';

interface DeploymentsListProps {
  deployments: DeploymentDTO[];
}

type DeploymentStatus = 'all' | 'success' | 'pending' | 'failed';

export function DeploymentsList({ deployments }: DeploymentsListProps) {
  const [statusFilter, setStatusFilter] = useState<DeploymentStatus>('all');

  const getStatus = (deployment: DeploymentDTO) => deployment.state ?? 'unknown';

  const filteredDeployments =
    statusFilter === 'all'
      ? deployments
      : deployments.filter((d) => getStatus(d) === statusFilter);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-emerald-500/10 border-emerald-500/20';
      case 'failed':
        return 'bg-red-500/10 border-red-500/20';
      case 'pending':
        return 'bg-amber-500/10 border-amber-500/20';
      default:
        return 'bg-slate-500/10 border-slate-500/20';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return (
          <Badge className="gap-1 bg-emerald-600 hover:bg-emerald-700">
            <span className="w-2 h-2 bg-emerald-300 rounded-full animate-pulse" />
            Successful
          </Badge>
        );
      case 'failed':
        return (
          <Badge className="gap-1 bg-red-600 hover:bg-red-700">
            <span className="w-2 h-2 bg-red-300" />
            Failed
          </Badge>
        );
      case 'pending':
        return (
          <Badge className="gap-1 bg-amber-600 hover:bg-amber-700">
            <span className="w-2 h-2 bg-amber-300 rounded-full animate-pulse" />
            In Progress
          </Badge>
        );
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Status:</span>
        <div className="flex gap-2">
          {(['all', 'success', 'pending', 'failed'] as DeploymentStatus[]).map((status) => (
            <Button
              key={status}
              variant={statusFilter === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter(status)}
              className="capitalize"
            >
              {status}
            </Button>
          ))}
        </div>
        {statusFilter !== 'all' && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setStatusFilter('all')}
            className="gap-1"
          >
            <X className="w-3 h-3" />
            Clear
          </Button>
        )}
      </div>

      {/* Deployments List */}
      <div className="space-y-3">
        {filteredDeployments.length > 0 ? (
          filteredDeployments.map((deployment, index) => {
            const status = getStatus(deployment);
            const createdAt = deployment.created_at ? new Date(deployment.created_at) : null;
            const deploymentName = deployment.description || deployment.environment || 'Deployment';
            return (
            <Card
              key={deployment.dep_id ?? `${deployment.environment ?? 'deployment'}-${index}`}
              className={`p-4 border ${getStatusColor(status)} transition-all hover:shadow-md`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-3">
                    <h3 className="text-sm font-semibold text-foreground">{deploymentName}</h3>
                    {getStatusBadge(status)}
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                    <div>
                      <p className="text-muted-foreground">Branch</p>
                      <p className="font-medium text-foreground mt-0.5">{deployment.ref || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Commit</p>
                      <p className="font-mono text-foreground mt-0.5">
                        {deployment.sha ? deployment.sha.slice(0, 7) : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Author</p>
                      <p className="font-medium text-foreground mt-0.5">{deployment.creator || 'Unknown'}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Deployed</p>
                      <p className="font-medium text-foreground mt-0.5">
                        {createdAt
                          ? formatDistanceToNow(createdAt, { addSuffix: true })
                          : 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>

                {deployment.log_url && (
                  <a
                    href={deployment.log_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-shrink-0 p-2 hover:bg-background rounded-lg transition-colors"
                    title="Open deployment URL"
                  >
                    <ExternalLink className="w-5 h-5 text-primary" />
                  </a>
                )}
              </div>
            </Card>
          )})
        ) : (
          <Card className="p-8 text-center border-dashed">
            <p className="text-muted-foreground">
              {statusFilter === 'all'
                ? 'No deployments available'
                : `No ${statusFilter} deployments found`}
            </p>
          </Card>
        )}
      </div>

      {/* Summary Stats */}
      {deployments.length > 0 && (
        <Card className="p-4 bg-muted/50 border-border">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-emerald-600">
                {deployments.filter((d) => getStatus(d) === 'success').length}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Successful</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-600">
                {deployments.filter((d) => getStatus(d) === 'pending').length}
              </p>
              <p className="text-xs text-muted-foreground mt-1">In Progress</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">
                {deployments.filter((d) => getStatus(d) === 'failed').length}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Failed</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
