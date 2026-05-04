import { clickUpApi } from '@/apiClient';
import type { SaveTasksRequest, SaveTasksResponse, VerifiedTask } from '@/api/api';

export const saveInClickupService = {
  async saveTasks(
    spaceId: string,
    tasks: VerifiedTask[],
    options?: { ignoreNames?: boolean; ignoreMails?: boolean }
  ): Promise<SaveTasksResponse | null> {
    const payload: SaveTasksRequest = {
      space_id: spaceId,
      tasks,
      ignore_names: options?.ignoreNames ?? undefined,
      ignore_mails: options?.ignoreMails ?? undefined,
    };

    const response = await clickUpApi.saveTasksToClickupClickupSavePost(payload);
    return response.data
      ? {
          message: response.data.message ?? '',
          total_tasks: response.data.total_tasks ?? 0,
        }
      : null;
  },
};