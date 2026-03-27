import { clickUpApi } from '@/apiClient';
import type {
  ClickUpRepoRefDTO,
  ClickUpSpaceCreateDTO,
  ClickUpSpaceDetailDTO,
  ClickUpSpaceLightDTO,
  ClickUpSpaceUpdateDTO,
} from '@/api/api';
import { handleApiError } from './api-error';

export const clickUpService = {
  async getAllSpacesLight(): Promise<ClickUpSpaceLightDTO[]> {
    try {
      const response = await clickUpApi.getAllLightClickupLightGet();
      return response.data ?? [];
    } catch (error) {
      handleApiError(error, 'Unable to load ClickUp spaces');
      return [];
    }
  },
  async createSpace(space: ClickUpSpaceLightDTO): Promise<ClickUpSpaceLightDTO | null> {
    const payload: ClickUpSpaceCreateDTO = {
      name: space.name ?? null,
      space_code: space.space_code ?? null,
    };

    try {
      const response = await clickUpApi.createSpaceClickupPost(payload);
      return {
        id: response.data?.id ?? null,
        name: response.data?.name ?? null,
        space_code: response.data?.space_code ?? null,
        repo: null,
      };
    } catch (error) {
      handleApiError(error, 'Unable to create ClickUp space');
      return null;
    }
  },
  async updateSpace(space: ClickUpSpaceLightDTO): Promise<ClickUpSpaceLightDTO | null> {
    if (typeof space.id !== 'number') {
      handleApiError(new Error('Missing ClickUp space id'), 'Unable to update ClickUp space');
      return null;
    }

    const repoRef: ClickUpRepoRefDTO | null = space.repo
      ? {
          id: space.repo.id ?? null,
          url: space.repo.url ?? null,
        }
      : null;

    const payload: ClickUpSpaceUpdateDTO = {
      id: space.id,
      name: space.name ?? null,
      space_code: space.space_code ?? null,
      repo: repoRef,
    };

    try {
      const response = await clickUpApi.updateSpaceClickupSpaceIdPut(space.id, payload);
      return mapDetailToLight(response.data ?? null);
    } catch (error) {
      handleApiError(error, 'Unable to update ClickUp space');
      return null;
    }
  },
  async deleteSpace(spaceId: number): Promise<boolean> {
    try {
      const response = await clickUpApi.deleteSpaceClickupSpaceIdDelete(spaceId);
      return response.data ?? false;
    } catch (error) {
      handleApiError(error, 'Unable to delete ClickUp space');
      return false;
    }
  },
};

const mapDetailToLight = (detail: ClickUpSpaceDetailDTO | null): ClickUpSpaceLightDTO | null => {
  if (!detail) return null;
  return {
    id: detail.id ?? null,
    name: detail.name ?? null,
    space_code: detail.space_code ?? null,
    repo: detail.repo ?? null,
  };
};
