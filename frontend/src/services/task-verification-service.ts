import { clickUpTasksApi } from '@/apiClient';
import type { GeneratedTaskFromBacklog, GeneratedTaskFromSummary, VerifiedTaskFromBacklogRequest, VerifiedTaskFromBacklogResponse, VerifiedTaskFromSummaryRequest, VerifiedTaskFromSummaryResponse } from '@/api/api';

export const taskVerificationService = {
  async verifyTasksFromSummary(
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

  async verifyTasksFromBacklog(
    spaceId: string,
    tasks: GeneratedTaskFromBacklog[]
  ): Promise<VerifiedTaskFromBacklogResponse> {
    if (!spaceId?.trim()) throw new Error('Click up space code is required');
    
    const payload: VerifiedTaskFromBacklogRequest = {
      space_id: spaceId,
      tasks,
    };

    const response = await clickUpTasksApi.verifyTasksClickupTasksVerifyFromBacklogPost(payload);
    return response.data ?? { total: 0, tasks: [] };
  },
};