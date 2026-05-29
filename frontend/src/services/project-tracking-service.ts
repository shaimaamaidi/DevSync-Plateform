import {
  taskStatusCheckApi,
  projectStatusCheckApi,
  weeklyProjectSummaryApi,
  commitTraceabilityApi,
} from '@/apiClient';
import type {
  TaskSearchRequest,
  TaskSearchResponse,
  SynthesizedTaskStatusRequest,
  SynthesizedTaskStatusResult,
  ProjectSpaceRequest,
  ProjectStatusSummary,
  WeeklyProjectSummaryResponse,
  MappedCommitTaskRequest,
  MappedCommitTaskResponse,
} from '@/api/api';

export const projectTracingService = {

  // Use case 1: "Is this task really completed?"

  async searchTask(request: TaskSearchRequest): Promise<TaskSearchResponse | null> {
    if (!request.space_id?.trim()) throw new Error('ClickUp space ID is required');
    if (!request.description?.trim()) throw new Error('Search description is required');

    const response = await taskStatusCheckApi.searchTaskTaskStatusSearchPost(request);
    return response.data ?? null;
  },

  async synthesizeTaskStatus(request: SynthesizedTaskStatusRequest): Promise<SynthesizedTaskStatusResult | null> {
    if (!request.task) throw new Error('ClickUp task is required');
    if (!request.task.id?.trim()) throw new Error('ClickUp task ID is required');

    const response = await taskStatusCheckApi.synthesizeTaskStatusTaskStatusSynthesizePost(request);
    return response.data ?? null;
  },

  // Use case 2: "Give me the overall status of this project" 

  async getProjectStatus(request: ProjectSpaceRequest): Promise<ProjectStatusSummary | null> {
    if (!request.space_id?.trim()) throw new Error('ClickUp space ID is required');

    const response = await projectStatusCheckApi.checkProjectStatusProjectStatusStatusPost(request);
    return response.data ?? null;
  },

  // Use case 3: "What was completed this week?"

  async getWeeklySummary(request: ProjectSpaceRequest): Promise<WeeklyProjectSummaryResponse | null> {
    if (!request.space_id?.trim()) throw new Error('ClickUp space ID is required');

    const response = await weeklyProjectSummaryApi.summarizeWeeklyProjectWeeklySummarySummaryPost(request);
    return response.data ?? null;
  },

  // Use case 4: "Which task does this commit correspond to?"

  async findTaskByCommit(request: MappedCommitTaskRequest): Promise<MappedCommitTaskResponse | null> {
    if (!request.commit?.trim()) throw new Error('Commit message is required');
    if (!request.space_id?.trim()) throw new Error('ClickUp space ID is required');

    const response = await commitTraceabilityApi.findTaskByCommitCommitTraceabilityFindTaskByCommitPost(request);
    return response.data ?? null;
  },
};