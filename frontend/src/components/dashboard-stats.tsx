import type { GitRepoDetailDTO, MemberDTO } from '@/api/api';
import { Card } from '@/components/ui/shared-primitives/card';
import { GitBranch, Zap, Users } from 'lucide-react';
import { StatCardSkeleton } from './ui/loading-and-feedback/stat-card-skeleton';

interface DashboardStatsProps {
  repos: GitRepoDetailDTO[];
  members: MemberDTO[];
  isLoading?: boolean;
  userLoading?: boolean;
  isAdmin?: boolean;
}

const statConfigs = [
  { icon: GitBranch, iconBg: 'bg-indigo-500/10', iconColor: 'text-indigo-600' },
  { icon: Users, iconBg: 'bg-blue-500/10', iconColor: 'text-blue-600' },
  { icon: Zap, iconBg: 'bg-orange-500/10', iconColor: 'text-orange-600' },
];

export function DashboardStats({ repos, members, isLoading, userLoading, isAdmin }: DashboardStatsProps) {
  const totalMembers = members.length;
  const uniqueClickUpSpaces = new Set(
    repos
      .map((repo) => repo.clickup_space?.id ?? repo.clickup_space?.space_code ?? null)
      .filter((value) => value != null)
  ).size;

  if (userLoading)
    return (
      <div className="w-full h-36 rounded-xl border border-border bg-card animate-pulse" />
    );

  return isLoading ? (
    <div className={`grid grid-cols-1 md:grid-cols-2 ${isAdmin ? 'lg:grid-cols-3' : 'lg:grid-cols-2'} gap-4`}>
      {statConfigs.map((config, i) =>
        i === 1 && !isAdmin ? null : i === 2 ? <StatCardSkeleton key={i} {...config} /> : <StatCardSkeleton key={i} {...config} />
      )}
    </div>
  ) : (
    <div className={`grid grid-cols-1 md:grid-cols-2 ${isAdmin ? 'lg:grid-cols-3' : 'lg:grid-cols-2'} gap-4`}>
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

      {isAdmin && (
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
      )}

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
    </div>
  );
}