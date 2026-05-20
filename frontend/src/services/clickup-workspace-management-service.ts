import { clickUpStructureCreationApi } from '@/apiClient';
import type {
  AddStatusRequest,
  ClickUpListMetadata,
  ClickUpMemberInvitation,
  ClickUpSpaceDTO,
  ClickUpSpaceRegisterDTO,
  CreateFolderRequest,
  CreateListRequest,
  CreateSpaceRequest,
  FolderWithListsMetadata,
} from '@/api/api';

export const clickUpStructureManagementService = {
  async registerSpace(request: ClickUpSpaceRegisterDTO): Promise<ClickUpSpaceDTO | null> {
    if (!request.name?.trim()) throw new Error('Click up space name is required');
    if (!request.space_code?.trim()) throw new Error('Click up space code is required');
    if (request.ignore_name === undefined) request.ignore_name = false;

    const response = await clickUpStructureCreationApi.registerSpaceClickupStructureSpacesRegisterPost(request);
    return response.data?? null;
  },

  async createSpace(request: CreateSpaceRequest): Promise<ClickUpSpaceDTO | null> {
    if (!request.space_name?.trim()) throw new Error('Click up space name is required');

    const response = await clickUpStructureCreationApi.createSpaceClickupStructureSpacesPost(request);
    return response.data ?? null;
  },

  async deleteSpace(spaceId: number): Promise<boolean> {
    if (typeof spaceId !== 'number') throw new Error('Cannot delete space: space not found');

    const response = await clickUpStructureCreationApi.deleteSpaceClickupStructureSpacesSpaceIdDelete(spaceId);
    return response.data ?? false;
  },

  async inviteMember(request: ClickUpMemberInvitation): Promise<boolean> {
    if (!request.email?.trim()) throw new Error('Member email is required');
    if (!request.role) throw new Error('Member role is required');

    const response = await clickUpStructureCreationApi.inviteMemberClickupStructureMembersInvitePost(request);
    return response.data ?? false;
  },

  async removeMemberFromWorkspace(memberId: number): Promise<boolean> {
    if (typeof memberId !== 'number') throw new Error('Cannot delete member: member not found');

    const response = await clickUpStructureCreationApi.removeMemberFromWorkspaceClickupStructureMembersMemberIdDelete(memberId);
    return response.data ?? false;
  },

  async createFolder(request: CreateFolderRequest): Promise<FolderWithListsMetadata | null> {
    if (!request.space_id?.trim()) throw new Error('Click up space code is required');
    if (!request.name?.trim()) throw new Error('Folder name is required');

    const response = await clickUpStructureCreationApi.createFolderClickupStructureFoldersPost(request);
    return response.data ?? null;
  },

  async createList(request: CreateListRequest): Promise<ClickUpListMetadata | null> {
    if (!request.space_id?.trim()) throw new Error('Click up space code is required');
    if (!request.folder_id?.trim()) request.folder_id = null;
    if (!request.name?.trim()) request.name = 'List';
    
    const response = await clickUpStructureCreationApi.createListClickupStructureListsPost(request);
    return response.data ?? null;
  },

  async addStatus(request: AddStatusRequest): Promise<ClickUpListMetadata | null> {
    if (!request.list_id?.trim()) throw new Error('Click up list id is required');
    if (!request.status?.trim()) throw new Error('Status name is required');
    if (!request.color?.trim()) throw new Error('Status color is required');
    if (!request.type?.trim()) throw new Error('Status type is required');

    const response = await clickUpStructureCreationApi.addStatusClickupStructureListsListIdStatusesPost(request.list_id, request);
    return response.data ?? null;
  },
};