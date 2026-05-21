import { useEffect, useMemo, useState } from 'react';
import type { DeploymentDTO, GitRepoDetailDTO } from '@/api/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { AlertCircle, Search } from 'lucide-react';
import { DeploymentsList } from './ui/deployments-list';

interface DeploymentsTrackerProps {
  deployments: DeploymentDTO[];
  repos: GitRepoDetailDTO[];
  onLoadDeployments: (repoUrl: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;       
  onRetry?: () => void;
}

export function DeploymentsTracker({ 
  deployments, 
  repos, 
  onLoadDeployments, 
  isLoading ,
  error,
  onRetry,
}: DeploymentsTrackerProps) {
  const [searchUrl, setSearchUrl] = useState('');
  const [filteredDeployments, setFilteredDeployments] = useState<DeploymentDTO[]>(deployments);
  const [selectedRepoUrl, setSelectedRepoUrl] = useState('');

  const repoOptions = useMemo(
    () => repos.filter((repo) => typeof repo.url === 'string' && repo.url.length > 0),
    [repos]
  );

  const applySearchFilter = (query: string, data: DeploymentDTO[]) => {
    if (!query) return data;
    return data.filter(
      (dep) =>
        (dep.log_url || '').includes(query) ||
        (dep.description || dep.environment || '').toLowerCase().includes(query.toLowerCase()) ||
        (dep.ref || '').toLowerCase().includes(query.toLowerCase())
    );
  };

  useEffect(() => {
    setFilteredDeployments(applySearchFilter(searchUrl, deployments));
  }, [deployments, searchUrl]);

  const handleSearch = () => {
    setFilteredDeployments(applySearchFilter(searchUrl, deployments));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-foreground mb-4">Deployments</h2>
        <p className="text-muted-foreground mb-6">
          Track and manage all deployments by URL or repository name
        </p>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Select
            value={selectedRepoUrl || 'none'}
            onValueChange={async (value) => {
              if (value === 'none') {
                setSelectedRepoUrl('');
                setFilteredDeployments([]);
                return;
              }
              setSelectedRepoUrl(value);
              await onLoadDeployments(value);
            }}
          >
            <SelectTrigger className="w-full sm:w-72 bg-input border-border text-foreground">
              <SelectValue placeholder="Select a repository..." />
            </SelectTrigger>
            <SelectContent className="bg-card border-border">
              {repoOptions.length === 0 ? (
                <SelectItem value="none" disabled>
                  No repository available
                </SelectItem>
              ) : (
                <>
                <SelectItem value="none" className="text-muted-foreground hidden" disabled>
                  <span className="text-muted-foreground">No repository selected</span>
                </SelectItem>
                {repoOptions.map((repo) => (
                  <SelectItem key={repo.id ?? repo.url} value={repo.url as string}>
                    {repo.name ?? repo.url}
                  </SelectItem>
                ))}
                </>
              )}
            </SelectContent>
          </Select>
          <Input
            placeholder="Search by URL, deployment name, or branch..."
            value={searchUrl}
            onChange={(e) => setSearchUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1 bg-input border-border text-foreground placeholder:text-muted-foreground"
          />
          <Button onClick={handleSearch} className="gap-2">
            <Search className="w-4 h-4" />
            Search
          </Button>
        </div>
      </div>
      {isLoading ? (
        <Card className="p-6 border-border overflow-x-auto">
          <table className="w-full min-w-[500px]">
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
                        <div
                          key={j}
                          className="w-8 h-8 rounded-full bg-muted animate-pulse"
                        />
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
        </Card>
      ) : error ? (
        <Card className="p-12 border-border border-dashed text-center">
          <div className="flex flex-col items-center gap-3">
            <div className="flex items-center gap-2 text-destructive text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              Failed to load deployments.
            </div>
            <button
              onClick={() => onRetry?.()}
              className="text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground transition"
            >
              Try again
            </button>
          </div>
        </Card>
      ) : filteredDeployments.length > 0 ? (
          <DeploymentsList deployments={filteredDeployments} />
        ) : (
          <Card className="p-12 border-border border-dashed text-center">
            <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
            <p className="text-muted-foreground">
              {!selectedRepoUrl
                ? 'Select a repository to view deployments.'
                : searchUrl
                  ? 'No deployments found matching your search.'
                  : 'No deployments available.'}
            </p>
          </Card>
        )}
    </div>
  );
}
