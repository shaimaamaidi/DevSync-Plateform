import { memberApi } from '@/apiClient';
import type { MemberCreateDTO, MemberDTO, MemberUpdateDTO, MemberWithReposDTO } from '@/api/api';
import { handleApiError } from './api-error';

export const memberService = {
  async getAllWithRepos(): Promise<MemberWithReposDTO[]> {
    try {
      const response = await memberApi.getAllWithReposMemberAllWithReposGet();
      return response.data ?? [];
    } catch (error) {
      handleApiError(error, 'Unable to load members');
      return [];
    }
  },
  mapToMemberDTO(member: MemberWithReposDTO): MemberDTO {
    return {
      id: member.id ?? null,
      username: member.username ?? null,
      mail: member.mail ?? null,
    };
  },
  async createMember(member: MemberCreateDTO): Promise<MemberDTO | null> {
    const payload: MemberCreateDTO = {
      username: member.username ?? null,
      mail: member.mail ?? null,
      password: member.password ?? null,
    };

    try {
      const response = await memberApi.addMemberMemberPost(payload);
      return response.data ?? null;
    } catch (error) {
      handleApiError(error, 'Unable to create member');
      return null;
    }
  },
  async updateMember(member: MemberUpdateDTO): Promise<MemberDTO | null> {
    if (typeof member.id !== 'number') {
      handleApiError(new Error('Missing member id'), 'Unable to update member');
      return null;
    }

    const payload: MemberUpdateDTO = {
      id: member.id,
      username: member.username ?? null,
      mail: member.mail ?? null,
      password: member.password ?? undefined, 
    };

    try {
      const response = await memberApi.updateMemberMemberMemberIdPut(member.id, payload);
      return response.data
        ? {
            id: response.data.id ?? null,
            username: response.data.username ?? null,
            mail: response.data.mail ?? null,
          }
        : null;
    } catch (error) {
      handleApiError(error, 'Unable to update member');
      return null;
    }
  },
  async deleteMember(memberId: number): Promise<boolean> {
    try {
      const response = await memberApi.deleteMemberMemberMemberIdDelete(memberId);
      return response.data ?? false;
    } catch (error) {
      handleApiError(error, 'Unable to delete member');
      return false;
    }
  },
};
