import type { RepoMemberDTO } from '@/api/api';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ShieldCheck, Users } from 'lucide-react';

interface MembersListProps {
  members: RepoMemberDTO[];
}

export function MembersList({ members }: MembersListProps) {
  const getRoleBadgeColor = () =>
    'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-foreground flex items-center gap-2">
        <Users className="w-5 h-5 text-primary" />
        Team Members ({members.length})
      </h3>

      <div className="space-y-2">
        {members.map((member) => (
          <div
            key={member.id}
            className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Avatar className="w-10 h-10">
                <AvatarFallback className="bg-primary text-primary-foreground font-semibold">
                  {(member.username || 'M')[0].toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="font-medium text-foreground">{member.username}</p>
                <p className="text-xs text-muted-foreground">{member.mail || 'No email'}</p>
              </div>
            </div>
            <Badge className={getRoleBadgeColor()}>
              <ShieldCheck className="w-4 h-4" />
              <span className="ml-1">Member</span>
            </Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
