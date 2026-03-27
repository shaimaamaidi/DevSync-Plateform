import { useEffect, useState } from 'react';
import { DashboardStats } from '@/components/dashboard-stats';
import { MembersTable } from '@/components/members-table';
import { Navigation } from '@/components/navigation';
import { memberService } from '@/services/member-service';
import type { DeploymentDTO, GitRepoDetailDTO, MemberDTO } from '@/api/api';

export default function MembersPage() {
  const [members, setMembers] = useState<MemberDTO[]>([]);
  const [repos] = useState<GitRepoDetailDTO[]>([]);
  const [deployments] = useState<DeploymentDTO[]>([]);

  useEffect(() => {
    let isActive = true;

    const loadMembers = async () => {
      const membersData = await memberService.getAllWithRepos();
      if (!isActive) return;
      setMembers(membersData.map(memberService.mapToMemberDTO));
    };

    loadMembers();

    return () => {
      isActive = false;
    };
  }, []);

  const handleUpdate = async (updatedMember: MemberDTO) => {
    const nextMember = await memberService.updateMember(updatedMember);
    if (!nextMember) return;
    setMembers((prev) => prev.map((m) => (m.id === nextMember.id ? nextMember : m)));
  };

  const handleDelete = async (id: number) => {
    const deleted = await memberService.deleteMember(id);
    if (!deleted) return;
    setMembers((prev) => prev.filter((m) => m.id !== id));
  };

  const handleAdd = async (newMember: MemberDTO) => {
    const createdMember = await memberService.createMember(newMember);
    if (!createdMember) return;
    setMembers((prev) => [...prev, createdMember]);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <DashboardStats repos={repos} deployments={deployments} />

        <div className="my-8 border-t border-border" />

        <MembersTable
          members={members}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
          onAdd={handleAdd}
        />
      </main>
    </div>
  );
}
