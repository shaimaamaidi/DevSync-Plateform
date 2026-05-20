import { clickUpTasksApi } from '@/apiClient';
import type { SaveTasksRequest, VerifiedTask } from '@/api/api';

export const saveInClickupService = {
  async saveTasks(
    spaceId: string,
    tasks: VerifiedTask[],
    options?: { ignoreNames?: boolean; ignoreMails?: boolean }
  ): Promise<boolean> {
    if (!spaceId?.trim()) throw new Error('Click up space code is required');
    const payload: SaveTasksRequest = {
      space_id: spaceId,
      tasks,
      ignore_names: options?.ignoreNames ?? false,
      ignore_mails: options?.ignoreMails ?? false,
    };

    await clickUpTasksApi.saveTasksToClickupClickupTasksSavePost(payload);

    return true;
  },
};