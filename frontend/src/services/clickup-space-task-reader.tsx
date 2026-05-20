import type { FolderWithLists } from "@/api/api";
import { clickUpTasksApi } from "@/apiClient";

export const clickupSpaceTaskReaderService = {
    async getTasksBySpace(spaceId: string): Promise<FolderWithLists[]> {
        if (!spaceId?.trim()) throw new Error('Click up space code is required');

        const response = await clickUpTasksApi.getTasksBySpaceClickupTasksSpacesSpaceIdGet(spaceId);
        return response.data ?? [];
    },
};