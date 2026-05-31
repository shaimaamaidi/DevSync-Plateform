import { clickUpTasksApi } from '@/apiClient';
import type { SaveBacklogTasksRequest, SaveSummaryTasksRequest, TaskSyncResult, VerifiedTaskFromBacklog, VerifiedTaskFromSummary } from '@/api/api';

export const saveInClickupService = {
  async saveTasksFromSummary(
    spaceId: string,
    tasks: VerifiedTaskFromSummary[],
    options?: { ignoreNames?: boolean; ignoreMails?: boolean }
  ): Promise<TaskSyncResult> {
    if (!spaceId?.trim()) throw new Error('Click up space code is required');
    const payload: SaveSummaryTasksRequest = {
      space_id: spaceId,
      tasks,
      ignore_names: options?.ignoreNames ?? false,
      ignore_mails: options?.ignoreMails ?? false,
    };

    const response = await clickUpTasksApi.saveSummaryTasksToClickupClickupTasksSaveSummaryTasksPost(payload);

    return response.data ?? null;
  },

  async saveTasksFromBacklog(
    spaceId: string,
    tasks: Array<VerifiedTaskFromBacklog>,
    options?: { ignoreNames?: boolean; ignoreMails?: boolean }
  ): Promise<TaskSyncResult> {
    if (!spaceId?.trim()) throw new Error('Click up space code is required');
    const payload: SaveBacklogTasksRequest = {
      space_id: spaceId,
      tasks,
      ignore_names: options?.ignoreNames ?? false,
      ignore_mails: options?.ignoreMails ?? false,
    };

    const response = await clickUpTasksApi.saveBacklogTasksToClickupClickupTasksSaveBacklogTasksPost(payload);

    return response.data ?? null;
  },  
};