import { repoApi } from '@/apiClient';
import type {
  GitRepoCreateDTO,
  GitRepoDetailDTO,
  GitRepoDTO,
  GitRepoUpdateDTO,
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

  async createRepo(repo: GitRepoCreateDTO): Promise<GitRepoDetailDTO | null> {
    const response = await repoApi.addRepoRepoPost(repo);
    const created = response.data ?? null;
    if (created?.id != null) {
      return await repoService.getRepoById(created.id);
    }

    return {
      id: created?.id ?? null,
      name: created?.name ?? created.name ?? null,
      url: created?.url ?? created.url ?? null,
      members: [],
      clickup_space: null,
    } as GitRepoDetailDTO;
  },

  async updateRepo(repo: GitRepoUpdateDTO): Promise<GitRepoDetailDTO | null> {
    if (typeof repo.id !== 'number') {
      throw new Error('Missing repository id');
    }
    const response = await repoApi.updateRepoRepoRepoIdPut(repo.id, repo);
    return response.data as GitRepoDetailDTO ?? null;
  },

  async deleteRepo(repoId: number): Promise<boolean> {
    const response = await repoApi.deleteRepoRepoRepoIdDelete(repoId);
    return response.data ?? false;
  },
};
