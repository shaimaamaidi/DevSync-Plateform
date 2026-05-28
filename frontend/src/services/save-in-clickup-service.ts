import { clickUpTasksApi } from '@/apiClient';
import type { SaveBacklogTasksRequest, SaveSummaryTasksRequest, VerifiedTaskFromBacklog, VerifiedTaskFromSummary } from '@/api/api';

export const saveInClickupService = {
  async saveTasksFromSummary(
    spaceId: string,
    tasks: VerifiedTaskFromSummary[],
    options?: { ignoreNames?: boolean; ignoreMails?: boolean }
  ): Promise<boolean> {
    if (!spaceId?.trim()) throw new Error('Click up space code is required');
    const payload: SaveSummaryTasksRequest = {
      space_id: spaceId,
      tasks,
      ignore_names: options?.ignoreNames ?? false,
      ignore_mails: options?.ignoreMails ?? false,
    };

    await clickUpTasksApi.saveSummaryTasksToClickupClickupTasksSaveSummaryTasksPost(payload);

    return true;
  },

  async saveTasksFromBacklog(
    spaceId: string,
    tasks: Array<VerifiedTaskFromBacklog>,
    options?: { ignoreNames?: boolean; ignoreMails?: boolean }
  ): Promise<boolean> {
    if (!spaceId?.trim()) throw new Error('Click up space code is required');
    const payload: SaveBacklogTasksRequest = {
      space_id: spaceId,
      tasks,
      ignore_names: options?.ignoreNames ?? false,
      ignore_mails: options?.ignoreMails ?? false,
    };

    await clickUpTasksApi.saveBacklogTasksToClickupClickupTasksSaveBacklogTasksPost(payload);

    return true;
  },  
};