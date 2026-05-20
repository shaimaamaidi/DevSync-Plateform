import { deploymentApi } from '@/apiClient';
import type { DeploymentDTO } from '@/api/api';
import { repoService } from './repo-service';

export const deploymentService = {
  async listByRepoUrl(repoUrl: string): Promise<DeploymentDTO[]> {
    if (!repoUrl?.trim()) throw new Error('Repository URL is required');

    const response = await deploymentApi.listDeploymentsDeploymentListGet(repoUrl);
    return response.data ?? [];
  },

  async listAll(): Promise<DeploymentDTO[]> {
    const repos = await repoService.getAllReposWithDetails();
    const allDeployments: DeploymentDTO[] = [];
    for (const repo of repos) {
      if (repo.url) {
        const deployments = await deploymentApi.listDeploymentsDeploymentListGet(repo.url);
        if (deployments.data) {
          allDeployments.push(...deployments.data);
        }
      }
    }
    return allDeployments;
  },
};
