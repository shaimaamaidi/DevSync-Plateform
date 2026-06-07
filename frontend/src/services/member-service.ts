import { memberApi } from '@/apiClient';
import type { 
  MemberCreateDTO, 
  MemberDTO, 
  MemberUpdateDTO, 
  MemberWithReposDTO 
} from '@/api/api';

export const memberService = {
  mapToMemberDTO(member: MemberWithReposDTO): MemberDTO {
    return {
      id: member.id,
      username: member.username,
      arabic_name: member.arabic_name,
      mail: member.mail,
      role: member.role,
    } as MemberDTO;
  },

  async getAllWithRepos(): Promise<MemberWithReposDTO[]> {
    const response = await memberApi.getAllWithReposMemberAllWithReposGet();
    return response.data ?? [];
  },

  async createMember(member: MemberCreateDTO): Promise<MemberDTO | null> {
    if (!member.username?.trim()) throw new Error('Username is required');
    if (!member.arabic_name?.trim()) throw new Error('Arabic name is required');
    if (!member.mail?.trim()) throw new Error('Email is required');
    if(!member.role) throw new Error('Role is required');
    if (!member.password?.trim()) throw new Error('Password is required');

    const response = await memberApi.addMemberMemberPost(member);
    return response.data as MemberDTO ?? null;
  },

  async updateMember(member: MemberUpdateDTO): Promise<MemberDTO | null> {
    if (typeof member.id !== 'number') throw new Error('Cannot update member: member not found');

    const hasUpdate =
    member.username?.trim() ||
    member.arabic_name?.trim() ||
    member.mail?.trim() ||
    member.password?.trim() || 
    member.role ||
    member.repos != null;

    if (!hasUpdate) throw new Error('At least one field must be provided to update a member');

    const response = await memberApi.updateMemberMemberMemberIdPut(member.id, member);
    return response.data as MemberDTO ?? null;
  },

  async deleteMember(memberId: number): Promise<boolean> {
    if (typeof memberId !== 'number') throw new Error('Cannot delete member: member not found');

    const response = await memberApi.deleteMemberMemberMemberIdDelete(memberId);
    return response.data ?? false;
  },
};
