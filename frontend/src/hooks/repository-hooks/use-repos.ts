import { useQuery } from '@tanstack/react-query';
import { repoService } from '@/services/repo-service';
import type { GitRepoDetailDTO } from '@/api/api';
import { defaultOnError } from '@/services/api-error';
import { extractStatusCode, resolveErrorAction, normalizeErrorMessage, extractErrorCode } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

export function useRepos() {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const { data, isLoading, isFetching, isError, refetch } = useQuery<GitRepoDetailDTO[] | null>({
    queryKey: ['repos'],
    queryFn: async () => {
      try{
        const data = await repoService.getAllReposWithDetails();
        return data;
      } catch (err) {
        const action = resolveErrorAction(err);
        const message = normalizeErrorMessage(err);
        const code = extractErrorCode(err);
        const status = extractStatusCode(err);
        await onError()(action, message, { code, status: status ?? undefined });
        throw err;
      }
    },
  });

  return {
    repos: data ?? [],
    loading: isLoading,
    isFetching,
    error: isError ? 'Unable to load repositories.' : null,
    refetch
  };
}