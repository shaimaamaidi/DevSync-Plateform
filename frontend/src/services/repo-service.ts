import { repoApi } from '@/apiClient';
import type {
  GitRepoCreateDTO,
  GitRepoDetailDTO,
  GitRepoDTO,
  GitRepoUpdateDTO,
  RepoClickUpSpaceRefDTO,
  RepoMemberRefDTO,
} from '@/api/api';

export const repoService = {
  async getAllRepos(): Promise<GitRepoDTO[]> {
    const response = await repoApi.getAllReposRepoAllGet();
    return response.data ?? [];
  },
  
  async getAllReposWithDetails(): Promise<GitRepoDetailDTO[]> {
    const response = await repoApi.getAllWithDetailsRepoDetailsGet();
    return response.data ?? [];
  },
  
  async getRepoById(repoId: number): Promise<GitRepoDetailDTO | null> {
    const response = await repoApi.getRepoByIdRepoRepoIdGet(repoId);
    return response.data ?? null;
  },

  async createRepo(repo: GitRepoDetailDTO): Promise<GitRepoDetailDTO | null> {
    const payload: GitRepoCreateDTO = {
      name: repo.name ?? null,
      url: repo.url ?? null,
    };

    const response = await repoApi.addRepoRepoPost(payload);
    const created = response.data ?? null;
    if (created?.id != null) {
      return await repoService.getRepoById(created.id);
    }

    return {
      id: created?.id ?? null,
      name: created?.name ?? payload.name ?? null,
      url: created?.url ?? payload.url ?? null,
      members: [],
      clickup_space: null,
    };
  },

  async updateRepo(repo: GitRepoDetailDTO): Promise<GitRepoDetailDTO | null> {
    if (typeof repo.id !== 'number') {
      throw new Error('Missing repository id');
    }
    const members: RepoMemberRefDTO[] | null = repo.members
      ? repo.members.map((member) => ({
          id: member.id ?? undefined,
          mail: member.mail ?? undefined,
        }))
      : null;

    const clickupSpace: RepoClickUpSpaceRefDTO | null = repo.clickup_space
      ? {
          id: repo.clickup_space.id ?? undefined,
          space_code: repo.clickup_space.space_code ?? undefined,
        }
      : null;

    const payload: GitRepoUpdateDTO = {
      id: repo.id,
      name: repo.name ?? null,
      url: repo.url ?? null,
      members,
      clickup_space: clickupSpace,
    };

    const payloadWithId = { ...payload, id: repo.id };
    const response = await repoApi.updateRepoRepoRepoIdPut(repo.id, payloadWithId);
    return response.data ?? null;
  },

  async deleteRepo(repoId: number): Promise<boolean> {
    const response = await repoApi.deleteRepoRepoRepoIdDelete(repoId);
    return response.data ?? false;
  },
};
