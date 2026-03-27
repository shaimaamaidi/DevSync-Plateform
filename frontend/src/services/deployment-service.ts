import { deploymentApi } from '@/apiClient';
import type { DeploymentDTO } from '@/api/api';
import { handleApiError } from './api-error';

export const deploymentService = {
  async listByRepoUrl(repoUrl: string): Promise<DeploymentDTO[]> {
    try {
      const response = await deploymentApi.listDeploymentsDeploymentListGet(repoUrl);
      return response.data ?? [];
    } catch (error) {
      handleApiError(error, 'Unable to load deployments');
      return [];
    }
  },
};
