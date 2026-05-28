import { clickUpTasksApi } from '@/apiClient';
import type { SaveSummaryTasksRequest, VerifiedTaskFromSummary } from '@/api/api';

export const saveInClickupService = {
  async saveTasks(
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
};