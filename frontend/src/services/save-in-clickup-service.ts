import { clickUpTasksApi } from '@/apiClient';
import type { SaveTasksRequest, VerifiedTask } from '@/api/api';

export const saveInClickupService = {
  async saveTasks(
    spaceId: string,
    tasks: VerifiedTask[],
    options?: { ignoreNames?: boolean; ignoreMails?: boolean }
  ): Promise<boolean> {
    const payload: SaveTasksRequest = {
      space_id: spaceId,
      tasks,
      ignore_names: options?.ignoreNames ?? undefined,
      ignore_mails: options?.ignoreMails ?? undefined,
    };

    await clickUpTasksApi.saveTasksToClickupClickupTasksSavePost(payload);

    // Si aucune erreur n’est levée → succès
    return true;
  },
};