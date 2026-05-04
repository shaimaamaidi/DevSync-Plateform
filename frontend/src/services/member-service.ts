import { memberApi } from '@/apiClient';
import type { MemberCreateDTO, MemberDTO, MemberUpdateDTO, MemberWithReposDTO } from '@/api/api';

export const memberService = {
  mapToMemberDTO(member: MemberWithReposDTO): MemberDTO {
    return {
      id: member.id ?? null,
      username: member.username ?? null,
      arabic_name: member.arabic_name ?? null,
      mail: member.mail ?? null,
    } as MemberDTO;
  },

  async getAllWithRepos(): Promise<MemberWithReposDTO[]> {
    const response = await memberApi.getAllWithReposMemberAllWithReposGet();
    return response.data ?? [];
  },

  async createMember(member: MemberCreateDTO): Promise<MemberDTO | null> {
    const payload: MemberCreateDTO = {
      username: member.username ?? null,
      arabic_name: member.arabic_name ?? null, 
      mail: member.mail ?? null,
      password: member.password ?? null,
    };

    const response = await memberApi.addMemberMemberPost(payload);
    return response.data as MemberDTO ?? null;
  },

  async updateMember(member: MemberUpdateDTO): Promise<MemberDTO | null> {
    if (typeof member.id !== 'number') {
      throw new Error('Missing member id');
    }

    const payload: MemberUpdateDTO = {
      id: member.id,
      username: member.username ?? null,
      arabic_name: member.arabic_name ?? null,
      mail: member.mail ?? null,
      password: member.password ?? undefined, 
    };

    const response = await memberApi.updateMemberMemberMemberIdPut(member.id, payload);
    return response.data
      ? {
          id: response.data.id ?? null,
          username: response.data.username ?? null,
          arabic_name: response.data.arabic_name ?? null,
          mail: response.data.mail ?? null,
        } as MemberDTO
      : null;
  },

  async deleteMember(memberId: number): Promise<boolean> {
    const response = await memberApi.deleteMemberMemberMemberIdDelete(memberId);
    return response.data ?? false;
  },
};
