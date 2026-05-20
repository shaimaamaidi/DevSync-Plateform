import { clickUpStructureMetadataApi } from '@/apiClient';
import type { FolderWithListsMetadata } from '@/api/api';

export const clickUpStructureMetadataService = {
  async getSpaceStructure(spaceId: string): Promise<FolderWithListsMetadata[]> {
    if (!spaceId?.trim()) throw new Error('Click up space code is required');

    const response = await clickUpStructureMetadataApi.getSpaceStructureMetadataClickupStructureSpacesSpaceIdMetadataGet(spaceId);
    return response.data ?? [];
  },
};