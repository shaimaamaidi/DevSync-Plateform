import {
  AssociatorApi,
  ClickUpApi,
  Configuration,
  DeploymentApi,
  MemberApi,
  RepoApi,
  ClickUpTasksApi,
  ClickUpStructureCreationApi,
  ClickUpStructureMetadataApi,
  TaskStatusCheckApi,
  ProjectStatusCheckApi,
  WeeklyProjectSummaryApi,
  CommitTraceabilityApi,
} from './api';
import { setupAxiosInterceptors } from './api/axios-interceptor';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export const apiConfig = new Configuration({
  basePath: apiBaseUrl,
});

setupAxiosInterceptors();

export const associatorApi = new AssociatorApi(apiConfig);
export const clickUpApi = new ClickUpApi(apiConfig);
export const deploymentApi = new DeploymentApi(apiConfig);
export const memberApi = new MemberApi(apiConfig);
export const repoApi = new RepoApi(apiConfig);
export const clickUpTasksApi = new ClickUpTasksApi(apiConfig);
export const clickUpStructureCreationApi = new ClickUpStructureCreationApi(apiConfig);
export const clickUpStructureMetadataApi = new ClickUpStructureMetadataApi(apiConfig);
export const taskStatusCheckApi = new TaskStatusCheckApi(apiConfig);
export const projectStatusCheckApi = new ProjectStatusCheckApi(apiConfig);
export const weeklyProjectSummaryApi = new WeeklyProjectSummaryApi(apiConfig);
export const commitTraceabilityApi = new CommitTraceabilityApi(apiConfig);