import { clickUpTasksApi } from '@/apiClient';
import type { GeneratedTask, VerifyTasksRequest, VerifyTasksResponse } from '@/api/api';

export const taskVerificationService = {
  async verifyTasks(
    spaceId: string,
    tasks: GeneratedTask[]
  ): Promise<VerifyTasksResponse> {
    const payload: VerifyTasksRequest = {
      space_id: spaceId,
      tasks,
    };

    const response = await clickUpTasksApi.verifyTasksClickupTasksVerifyPost(payload);
    return response.data ?? { total: 0, tasks: [] };
  },
};