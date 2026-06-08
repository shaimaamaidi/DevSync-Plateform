import { useState, useCallback } from 'react';
import type { DeploymentDTO } from '@/api/api';

export function useDeployments(initialDeployments: DeploymentDTO[] = []) {
  const [deployments, setDeployments] = useState<DeploymentDTO[]>(initialDeployments);

  const addDeployment = useCallback((newDeployment: DeploymentDTO) => {
    setDeployments((prevDeployments) => [newDeployment, ...prevDeployments]);
  }, []);

  const updateDeployment = useCallback((id: string, updates: Partial<DeploymentDTO>) => {
    setDeployments((prevDeployments) =>
      prevDeployments.map((dep) =>
        dep.dep_id === id ? { ...dep, ...updates } : dep
      )
    );
  }, []);

  const getDeploymentsByStatus = useCallback(
    (status: 'success' | 'failed' | 'pending') => {
      return deployments.filter((d) => d.state === status);
    },
    [deployments]
  );

  const getSuccessRate = useCallback(() => {
    if (deployments.length === 0) return 0;
    const successful = deployments.filter((d) => d.state === 'success').length;
    return Math.round((successful / deployments.length) * 100);
  }, [deployments]);

  const getRecentDeployments = useCallback((count: number = 5) => {
    return [...deployments].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    ).slice(0, count);
  }, [deployments]);

  return {
    deployments,
    addDeployment,
    updateDeployment,
    getDeploymentsByStatus,
    getSuccessRate,
    getRecentDeployments,
  };
}
