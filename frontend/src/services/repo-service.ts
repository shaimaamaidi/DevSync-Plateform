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
    if (typeof repoId !== 'number') throw new Error('Cannot get repo: repo not found');
    
    const response = await repoApi.getRepoByIdRepoRepoIdGet(repoId);
    return response.data ?? null;
  },

  async createRepo(repo: GitRepoCreateDTO): Promise<GitRepoDetailDTO | null> {
    if (!repo.name?.trim()) throw new Error('Repository name is required');
    if (!repo.url?.trim()) throw new Error('Repository URL is required');

    const response = await repoApi.addRepoRepoPost(repo);
    const created = response.data ?? null;
    if (created?.id != null) {
      return await repoService.getRepoById(created.id);
    }

    return {
      id: created?.id ,
      name: created?.name ?? created.name,
      url: created?.url ?? created.url,
      members: [],
      clickup_space: null,
    } as GitRepoDetailDTO;
  },

  async updateRepo(repo: GitRepoUpdateDTO): Promise<GitRepoDetailDTO | null> {
    if (typeof repo.id !== 'number') throw new Error('Cannot update repo: repo not found');

    const hasUpdate =
    repo.name?.trim() ||
    repo.url?.trim() ||
    repo.members != null ||
    repo.clickup_space != null;

    if (!hasUpdate) throw new Error('At least one field must be provided to update a repository');

    const response = await repoApi.updateRepoRepoRepoIdPut(repo.id, repo);
    return response.data as GitRepoDetailDTO ?? null;
  },

  async deleteRepo(repoId: number): Promise<boolean> {
    if (typeof repoId !== 'number') throw new Error('Cannot delete repo: repo not found');
    
    const response = await repoApi.deleteRepoRepoRepoIdDelete(repoId);
    return response.data ?? false;
  },
};
