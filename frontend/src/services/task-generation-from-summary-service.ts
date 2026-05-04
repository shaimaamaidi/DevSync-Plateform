import { clickUpApi } from '@/apiClient';
import type { GenerateTasksFromSummaryRequest, GeneratedTask } from '@/api/api';

export const taskGenerationService = {
  async generateFromSummary(
    meetingSummary: string,
    spaceId: string
  ): Promise<GeneratedTask[]> {
    const payload: GenerateTasksFromSummaryRequest = {
      meeting_summary: meetingSummary,
      space_id: spaceId,
    };

    const response =
      await clickUpApi.generateTasksFromSummaryClickupGenerateTasksFromSummaryPost(payload);
    return response.data ?? [];
  },
};