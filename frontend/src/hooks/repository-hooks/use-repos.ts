import { useQuery } from '@tanstack/react-query';
import { repoService } from '@/services/repo-service';
import type { GitRepoDetailDTO } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useRepos() {
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  const { data, isLoading, isError } = useQuery<GitRepoDetailDTO[] | null>({
    queryKey: ['repos'],
    queryFn: async () => {
      const data = await withErrorHandling(
        () => repoService.getAllReposWithDetails(),
        'Load GitHub repositories',
        onError,
      );
      return data;
    },
  });

  return {
    repos: data ?? [],
    loading: isLoading,
    error: isError ? 'Unable to load repositories' : null,
  };
}