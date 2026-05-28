import { clickUpTasksApi } from '@/apiClient';
import type { GeneratedTaskFromSummary, VerifiedTaskFromSummaryRequest, VerifiedTaskFromSummaryResponse } from '@/api/api';

export const taskVerificationService = {
  async verifyTasks(
    spaceId: string,
    tasks: GeneratedTaskFromSummary[]
  ): Promise<VerifiedTaskFromSummaryResponse> {
    if (!spaceId?.trim()) throw new Error('Click up space code is required');
    const payload: VerifiedTaskFromSummaryRequest = {
      space_id: spaceId,
      tasks,
    };

    const response = await clickUpTasksApi.verifyTasksClickupTasksVerifyFromSummaryPost(payload);
    return response.data ?? { total: 0, tasks: [] };
  },
};