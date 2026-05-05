import { clickUpStructureMetadataApi } from '@/apiClient';
import type { FolderWithListsMetadata } from '@/api/api';

export const clickUpStructureMetadataService = {
  async getSpaceStructure(spaceId: string): Promise<FolderWithListsMetadata[]> {
    if (!spaceId) {
      throw new Error('Missing space id');
    }

    const response = await clickUpStructureMetadataApi.getSpaceStructureMetadataClickupStructureSpacesSpaceIdMetadataGet(spaceId);
    return response.data ?? [];
  },
};