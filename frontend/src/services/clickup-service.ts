import { clickUpApi } from '@/apiClient';
import type {
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

  async createSpace(space: ClickUpSpaceCreateDTO): Promise<ClickUpSpaceLightDTO | null> {
    const response = await clickUpApi.createSpaceClickupPost(space);
    return {
      id: response.data?.id ?? null,
      name: response.data?.name ?? null,
      space_code: response.data?.space_code ?? null,
      repo: null,
    } as ClickUpSpaceLightDTO;
  },

  async updateSpace(space: ClickUpSpaceUpdateDTO): Promise<ClickUpSpaceLightDTO | null> {
    if (typeof space.id !== 'number') {
      throw new Error('Missing ClickUp space id');
    }

    const response = await clickUpApi.updateSpaceClickupSpaceIdPut(space.id, space);
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
