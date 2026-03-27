import { useEffect, useMemo, useState } from 'react';
import type { DeploymentDTO, GitRepoDetailDTO } from '@/api/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search } from 'lucide-react';
import { DeploymentsList } from './deployments-list';

interface DeploymentsTrackerProps {
  deployments: DeploymentDTO[];
  repos: GitRepoDetailDTO[];
  onLoadDeployments: (repoUrl: string) => Promise<void>;
}

export function DeploymentsTracker({ deployments, repos, onLoadDeployments }: DeploymentsTrackerProps) {
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
        <h2 className="text-2xl font-bold text-foreground mb-4">Deployments</h2>
        <p className="text-muted-foreground mb-6">
          Track and manage all deployments by URL or repository name
        </p>

        {/* Search Bar */}
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
              <SelectItem value="none">No repository</SelectItem>
              {repoOptions.map((repo) => (
                <SelectItem key={repo.id ?? repo.url} value={repo.url as string}>
                  {repo.name ?? repo.url}
                </SelectItem>
              ))}
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

      {/* Deployments List Component */}
      {filteredDeployments.length > 0 ? (
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
