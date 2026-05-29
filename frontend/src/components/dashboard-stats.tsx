import type { DeploymentDTO, GitRepoDetailDTO, MemberDTO } from '@/api/api';
import { Card } from '@/components/ui/shared-primitives/card';
import { GitBranch, Zap, Users, CheckCircle } from 'lucide-react';
import { StatCardSkeleton } from './ui/loading-and-feedback/stat-card-skeleton';

interface DashboardStatsProps {
  repos: GitRepoDetailDTO[];
  deployments: DeploymentDTO[];
  members: MemberDTO[];
  isLoading?: boolean;
}

const statConfigs = [
  { icon: GitBranch, iconBg: 'bg-indigo-500/10', iconColor: 'text-indigo-600' },
  { icon: Users, iconBg: 'bg-blue-500/10', iconColor: 'text-blue-600' },
  { icon: Zap, iconBg: 'bg-orange-500/10', iconColor: 'text-orange-600' },
  { icon: CheckCircle, iconBg: 'bg-green-500/10', iconColor: 'text-green-600' },
];

export function DashboardStats({ repos, deployments, members, isLoading }: DashboardStatsProps) {
  const totalMembers = members.length;
  const uniqueClickUpSpaces = new Set(
    repos
      .map((repo) => repo.clickup_space?.id ?? repo.clickup_space?.space_code ?? null)
      .filter((value) => value != null)
  ).size;
  const successfulDeployments = deployments.filter((d) => d.state === 'success').length;

  return (
    isLoading ? (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statConfigs.map((config, i) => (
          <StatCardSkeleton key={i} {...config} />
        ))}
      </div>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6 border-border hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div className="flex flex-col justify-between min-h-[88px]">
              <p className="text-sm text-muted-foreground font-medium">Total Repositories</p>
              <p className="text-2xl sm:text-3xl font-bold text-foreground mt-2">{repos.length}</p>
              <p className="text-xs text-muted-foreground mt-2 invisible">-</p>
            </div>
            <div className="p-3 bg-indigo-500/10 rounded-lg">
              <GitBranch className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-border hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div className="flex flex-col justify-between min-h-[88px]">
              <p className="text-sm text-muted-foreground font-medium">Team Members</p>
              <p className="text-2xl sm:text-3xl font-bold text-foreground mt-2">{totalMembers}</p>
              <p className="text-xs text-muted-foreground mt-2 invisible">-</p>
            </div>
            <div className="p-3 bg-blue-500/10 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-border hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground font-medium">ClickUp Spaces</p>
              <p className="text-2xl sm:text-3xl font-bold text-foreground mt-2">{uniqueClickUpSpaces}</p>
              <p className="text-xs text-muted-foreground mt-2">
                {repos.length > 0
                  ? Math.round(
                      (repos.filter((repo) => repo.clickup_space).length / repos.length) * 100
                    )
                  : 0}
                % repos assigned
              </p>
            </div>
            <div className="p-3 bg-orange-500/10 rounded-lg">
              <Zap className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-border hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground font-medium">Successful Deploys</p>
              <p className="text-2xl sm:text-3xl font-bold text-foreground mt-2">{successfulDeployments}</p>
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
    )
  );
}
