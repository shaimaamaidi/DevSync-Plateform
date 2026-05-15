import type { MemberDTO } from "@/api/api";
import { AvatarWithTooltip } from "./avatar-with-tool-tip";

interface AssigneeBadgesProps {
  assignee: string | null | undefined;
  members: MemberDTO[];
}

export function AssigneeBadges({ assignee, members }: AssigneeBadgesProps) {
  if (!assignee) return null;

  const mails = assignee
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  if (mails.length === 0) return null;

  const getDisplayName = (mail: string): string => {
    const member = members.find((m) => m.mail === mail);
    return member?.username ?? member?.arabic_name ?? mail.split("@")[0];
  };

  if (mails.length === 1) {
    const mail = mails[0];
    const name = getDisplayName(mail);
    return (
      <span className="inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground">
        <AvatarWithTooltip mail={mail} name={name} />
        <span className="truncate max-w-[120px]">{name}</span>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-md border bg-muted text-muted-foreground">
      <span className="flex -space-x-1">
        {mails.slice(0, 3).map((mail) => (
          <AvatarWithTooltip key={mail} mail={mail} name={getDisplayName(mail)} />
        ))}
      </span>
      <span>{mails.length} assignees</span>
    </span>
  );
}