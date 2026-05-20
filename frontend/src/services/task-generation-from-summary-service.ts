import { clickUpTasksApi } from '@/apiClient';
import type { GenerateTasksFromSummaryRequest, GeneratedTask } from '@/api/api';

export const taskGenerationService = {
  async generateFromSummary(
    meetingSummary: string,
    spaceId: string
  ): Promise<GeneratedTask[]> {
    if (!meetingSummary?.trim()) throw new Error('Meeting summary is required');
    if (!spaceId?.trim()) throw new Error('Click up space code is required');

    const payload: GenerateTasksFromSummaryRequest = {
      meeting_summary: meetingSummary,
      space_id: spaceId,
    };

    const response =
      await clickUpTasksApi.generateTasksFromSummaryClickupTasksGenerateTasksFromSummaryPost(payload);
    return response.data ?? [];
  },
};