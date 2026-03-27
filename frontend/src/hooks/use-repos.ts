import { useState, useCallback } from 'react';
import type { GitRepoDetailDTO } from '@/api/api';

export function useRepos(initialRepos: GitRepoDetailDTO[] = []) {
  const [repos, setRepos] = useState<GitRepoDetailDTO[]>(initialRepos);

  const updateRepo = useCallback((updatedRepo: GitRepoDetailDTO) => {
    setRepos((prevRepos) =>
      prevRepos.map((repo) => (repo.id === updatedRepo.id ? updatedRepo : repo))
    );
  }, []);

  const deleteRepo = useCallback((id: number) => {
    setRepos((prevRepos) => prevRepos.filter((repo) => repo.id !== id));
  }, []);

  const addRepo = useCallback((newRepo: GitRepoDetailDTO) => {
    setRepos((prevRepos) => [...prevRepos, newRepo]);
  }, []);

  const getRepoById = useCallback(
    (id: number) => repos.find((repo) => repo.id === id),
    [repos]
  );

  const getTotalMembers = useCallback(() => {
    return repos.reduce((acc, repo) => acc + (repo.members?.length ?? 0), 0);
  }, [repos]);

  const getAssignedToClickUp = useCallback(() => {
    return repos.filter((repo) => repo.clickup_space).length;
  }, [repos]);

  return {
    repos,
    updateRepo,
    deleteRepo,
    addRepo,
    getRepoById,
    getTotalMembers,
    getAssignedToClickUp,
  };
}
