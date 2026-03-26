import {
  AssociatorApi,
  ClickUpApi,
  Configuration,
  DeploymentApi,
  MemberApi,
  RepoApi,
} from './api';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export const apiConfig = new Configuration({
  basePath: apiBaseUrl,
});

export const associatorApi = new AssociatorApi(apiConfig);
export const clickUpApi = new ClickUpApi(apiConfig);
export const deploymentApi = new DeploymentApi(apiConfig);
export const memberApi = new MemberApi(apiConfig);
export const repoApi = new RepoApi(apiConfig);
