
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

  async listAll(): Promise<DeploymentDTO[]> {
    // On récupère tous les repos, puis on agrège tous les déploiements
    try {
      const { repoService } = await import('./repo-service');
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
    } catch (error) {
      handleApiError(error, 'Unable to load all deployments');
      return [];
    }
  },
};
