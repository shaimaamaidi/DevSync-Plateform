import type { FolderWithLists } from "@/api/api";
import { clickUpTasksApi } from "@/apiClient";

export const clickupSpaceTaskReaderService = {
    async getTasksBySpace(spaceId: string): Promise<FolderWithLists[]> {
        const response = await clickUpTasksApi.getTasksBySpaceClickupTasksSpacesSpaceIdGet(spaceId);
        return response.data ?? [];
    },
};