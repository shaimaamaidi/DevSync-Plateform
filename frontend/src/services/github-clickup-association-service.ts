import type { 
    AssociateClickUpSpaceRequest, 
    AssociateClickUpSpaceResponse 
} from "@/api/api";
import { associatorApi } from '@/apiClient';

export const gitHubClickUpAssociationService = {
    async associateRepoWithClickUp(request: AssociateClickUpSpaceRequest): Promise<AssociateClickUpSpaceResponse> {
        const response = await associatorApi.associateSpaceAssociateSpacePost(request);
        return response.data ?? null;
    }
}
