import type { 
    AssociateClickUpSpaceRequest, 
    AssociateClickUpSpaceResponse 
} from "@/api/api";
import { associatorApi } from '@/apiClient';

export const gitHubClickUpAssociationService = {
    async associateRepoWithClickUp(request: AssociateClickUpSpaceRequest): Promise<AssociateClickUpSpaceResponse> {
        if (!request.repo_url?.trim()) throw new Error('Repository URL is required');
        if (!request.space_code?.trim()) throw new Error('ClickUp space ID is required');

        const response = await associatorApi.associateSpaceAssociateSpacePost(request);
        return response.data ?? null;
    }
}
