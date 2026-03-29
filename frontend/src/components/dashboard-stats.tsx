import type { DeploymentDTO, GitRepoDetailDTO, MemberDTO } from '@/api/api';
import { Card } from '@/components/ui/card';
import { GitBranch, Zap, Users, CheckCircle } from 'lucide-react';

interface DashboardStatsProps {
  repos: GitRepoDetailDTO[];
  deployments: DeploymentDTO[];
  members: MemberDTO[];
}

export function DashboardStats({ repos, deployments, members }: DashboardStatsProps) {
  const totalMembers = members.length;
  const uniqueClickUpSpaces = new Set(
    repos
      .map((repo) => repo.clickup_space?.id ?? repo.clickup_space?.space_code ?? null)
      .filter((value) => value != null)
  ).size;
  const successfulDeployments = deployments.filter((d) => d.state === 'success').length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Repos */}
      <Card className="p-6 border-border hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground font-medium">Total Repositories</p>
            <p className="text-3xl font-bold text-foreground mt-2">{repos.length}</p>
          </div>
          <div className="p-3 bg-primary/10 rounded-lg">
            <GitBranch className="w-6 h-6 text-primary" />
          </div>
        </div>
      </Card>

      {/* Team Members */}
      <Card className="p-6 border-border hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground font-medium">Team Members</p>
            <p className="text-3xl font-bold text-foreground mt-2">{totalMembers}</p>
          </div>
          <div className="p-3 bg-blue-500/10 rounded-lg">
            <Users className="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </Card>

      {/* ClickUp Spaces */}
      <Card className="p-6 border-border hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground font-medium">ClickUp Spaces</p>
            <p className="text-3xl font-bold text-foreground mt-2">{uniqueClickUpSpaces}</p>
            <p className="text-xs text-muted-foreground mt-2">
              {repos.length > 0
                ? Math.round(
                    (repos.filter((repo) => repo.clickup_space).length / repos.length) * 100
                  )
                : 0}
              % repos assigned
            </p>
          </div>
          <div className="p-3 bg-purple-500/10 rounded-lg">
            <Zap className="w-6 h-6 text-purple-600" />
          </div>
        </div>
      </Card>

      {/* Successful Deployments */}
      <Card className="p-6 border-border hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground font-medium">Successful Deploys</p>
            <p className="text-3xl font-bold text-foreground mt-2">{successfulDeployments}</p>
            <p className="text-xs text-muted-foreground mt-2">
              {deployments.length > 0
                ? Math.round((successfulDeployments / deployments.length) * 100)
                : 0}
              % success rate
            </p>
          </div>
          <div className="p-3 bg-green-500/10 rounded-lg">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
        </div>
      </Card>
    </div>
  );
}
