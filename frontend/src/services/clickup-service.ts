import { clickUpApi } from '@/apiClient';
import type {
  ClickUpSpaceCreateDTO,
  ClickUpSpaceDetailDTO,
  ClickUpSpaceLightDTO,
  ClickUpSpaceUpdateDTO,
  RepoClickUpSpaceDTO,
} from '@/api/api';

export const clickUpService = {
  async getAllSpacesLight(): Promise<ClickUpSpaceLightDTO[]> {
    const response = await clickUpApi.getAllLightClickupLightGet();
    return response.data ?? [];
  },

  async getAllSpaces(): Promise<RepoClickUpSpaceDTO[]> {
    const response = await clickUpApi.getAllSpacesClickupGet();
    return response.data ?? [];
  },
  
  async createSpace(space: ClickUpSpaceCreateDTO): Promise<ClickUpSpaceLightDTO | null> {
    if (!space.name?.trim()) throw new Error('Click up space name is required');
    if (!space.space_code?.trim()) throw new Error('Click up space code is required');

    const response = await clickUpApi.createSpaceClickupPost(space);
    return mapDetailToLight(response.data ?? null);
  },

  async updateSpace(space: ClickUpSpaceUpdateDTO): Promise<ClickUpSpaceLightDTO | null> {
    if (typeof space.id !== 'number') throw new Error('Cannot update space: space not found');

    const hasUpdate =
    space.name?.trim() ||
    space.space_code?.trim() ||
    space.repo != null;

    if (!hasUpdate) throw new Error('At least one field must be provided to update a space');

    const response = await clickUpApi.updateSpaceClickupSpaceIdPut(space.id, space);
    return mapDetailToLight(response.data ?? null);
  },

  async deleteSpace(spaceId: number): Promise<boolean> {
    if (typeof spaceId !== 'number') throw new Error('Cannot delete space: space not found');

    const response = await clickUpApi.deleteSpaceClickupSpaceIdDelete(spaceId);
    return response.data ?? false;
  },
};

const mapDetailToLight = (detail: ClickUpSpaceDetailDTO | null): ClickUpSpaceLightDTO | null => {
  if (!detail) 
    return null;
  return {
    id: detail.id,
    name: detail.name,
    space_code: detail.space_code,
    repo: detail.repo ?? null,
  };
};
