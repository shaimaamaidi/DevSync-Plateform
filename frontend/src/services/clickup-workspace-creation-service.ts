import { clickUpStructureCreationApi } from '@/apiClient';
import type {
  AddStatusRequest,
  ClickUpListMetadata,
  ClickUpSpaceDTO,
  CreateFolderRequest,
  CreateListRequest,
  CreateSpaceRequest,
  FolderWithListsMetadata,
} from '@/api/api';

export const clickUpStructureCreationService = {
  async createSpace(request: CreateSpaceRequest): Promise<ClickUpSpaceDTO | null> {
    const payload: CreateSpaceRequest = {
      space_id: request.space_id,
    };

    const response = await clickUpStructureCreationApi.createSpaceClickupStructureSpacesPost(payload);
    return response.data ?? null;
  },

  async createFolder(request: CreateFolderRequest): Promise<FolderWithListsMetadata | null> {
    if (!request.space_id) {
      throw new Error('Missing space id');
    }

    const response = await clickUpStructureCreationApi.createFolderClickupStructureFoldersPost(request);
    return response.data ?? null;
  },

  async createList(request: CreateListRequest): Promise<ClickUpListMetadata | null> {
    if (!request.space_id || !request.name) {
      throw new Error('Missing space id or list name');
    }

    const response = await clickUpStructureCreationApi.createListClickupStructureListsPost(request);
    return response.data ?? null;
  },

  async addStatus(request: AddStatusRequest): Promise<ClickUpListMetadata | null> {
    if (!request.list_id || !request.status || !request.color || !request.type) {
      throw new Error('Missing list id or status information');
    }

    const response = await clickUpStructureCreationApi.addStatusClickupStructureListsListIdStatusesPost(request.list_id, request);
    return response.data ?? null;
  },
};