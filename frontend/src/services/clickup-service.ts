import { clickUpApi } from '@/apiClient';
import type {
  ClickUpRepoRefDTO,
  ClickUpSpaceCreateDTO,
  ClickUpSpaceDetailDTO,
  ClickUpSpaceLightDTO,
  ClickUpSpaceUpdateDTO,
} from '@/api/api';

export const clickUpService = {
  async getAllSpacesLight(): Promise<ClickUpSpaceLightDTO[]> {
    const response = await clickUpApi.getAllLightClickupLightGet();
    return response.data ?? [];
  },

  async createSpace(space: ClickUpSpaceLightDTO): Promise<ClickUpSpaceLightDTO | null> {
    const payload: ClickUpSpaceCreateDTO = {
      name: space.name ?? null,
      space_code: space.space_code ?? null,
    };

    const response = await clickUpApi.createSpaceClickupPost(payload);
    return {
      id: response.data?.id ?? null,
      name: response.data?.name ?? null,
      space_code: response.data?.space_code ?? null,
      repo: null,
    };
  },

  async updateSpace(space: ClickUpSpaceLightDTO): Promise<ClickUpSpaceLightDTO | null> {
    if (typeof space.id !== 'number') {
      throw new Error('Missing ClickUp space id');
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

    const response = await clickUpApi.updateSpaceClickupSpaceIdPut(space.id, payload);
    return mapDetailToLight(response.data ?? null);
  },

  async deleteSpace(spaceId: number): Promise<boolean> {
    const response = await clickUpApi.deleteSpaceClickupSpaceIdDelete(spaceId);
    return response.data ?? false;
  },
};

const mapDetailToLight = (detail: ClickUpSpaceDetailDTO | null): ClickUpSpaceLightDTO | null => {
  if (!detail) 
    return null;
  return {
    id: detail.id ?? null,
    name: detail.name ?? null,
    space_code: detail.space_code ?? null,
    repo: detail.repo ?? null,
  };
};
