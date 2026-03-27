import { repoApi } from '@/apiClient';
import type {
  GitRepoCreateDTO,
  GitRepoDetailDTO,
  GitRepoDTO,
  GitRepoUpdateDTO,
  RepoClickUpSpaceRefDTO,
  RepoMemberRefDTO,
} from '@/api/api';
import { handleApiError } from './api-error';

export const repoService = {
  async getAllRepos(): Promise<GitRepoDTO[]> {
    try {
      const response = await repoApi.getAllReposRepoAllGet();
      return response.data ?? [];
    } catch (error) {
      handleApiError(error, 'Unable to load repositories');
      return [];
    }
  },
  async getAllReposWithDetails(): Promise<GitRepoDetailDTO[]> {
    try {
      const response = await repoApi.getAllWithDetailsRepoDetailsGet();
      return response.data ?? [];
    } catch (error) {
      handleApiError(error, 'Unable to load repository details');
      return [];
    }
  },
  async getRepoById(repoId: number): Promise<GitRepoDetailDTO | null> {
    try {
      const response = await repoApi.getRepoByIdRepoRepoIdGet(repoId);
      return response.data ?? null;
    } catch (error) {
      handleApiError(error, 'Unable to load repository');
      return null;
    }
  },
  async createRepo(repo: GitRepoDetailDTO): Promise<GitRepoDetailDTO | null> {
    const payload: GitRepoCreateDTO = {
      name: repo.name ?? null,
      url: repo.url ?? null,
    };

    try {
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
    } catch (error) {
      handleApiError(error, 'Unable to create repository');
      return null;
    }
  },
  async updateRepo(repo: GitRepoDetailDTO): Promise<GitRepoDetailDTO | null> {
    if (typeof repo.id !== 'number') {
      handleApiError(new Error('Missing repository id'), 'Unable to update repository');
      return null;
    }

    const members: RepoMemberRefDTO[] | null = repo.members
      ? repo.members.map((member) => ({
          id: member.id ?? null,
          mail: member.mail ?? null,
        }))
      : null;

    const clickupSpace: RepoClickUpSpaceRefDTO | null = repo.clickup_space
      ? {
          id: repo.clickup_space.id ?? null,
          space_code: repo.clickup_space.space_code ?? null,
        }
      : null;

    const payload: GitRepoUpdateDTO = {
      id: repo.id,
      name: repo.name ?? null,
      url: repo.url ?? null,
      members,
      clickup_space: clickupSpace,
    };

    try {
      const response = await repoApi.updateRepoRepoRepoIdPut(repo.id, payload);
      return response.data ?? null;
    } catch (error) {
      handleApiError(error, 'Unable to update repository');
      return null;
    }
  },
  async deleteRepo(repoId: number): Promise<boolean> {
    try {
      const response = await repoApi.deleteRepoRepoRepoIdDelete(repoId);
      return response.data ?? false;
    } catch (error) {
      handleApiError(error, 'Unable to delete repository');
      return false;
    }
  },
};
