import { useMutation, useQueryClient } from '@tanstack/react-query';
import { repoService } from '@/services/repo-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import type { GitRepoUpdateDTO } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useUpdateRepo() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  return useMutation({
    mutationFn: async (repo: GitRepoUpdateDTO) => {
      const result = await withErrorHandling(
        () => repoService.updateRepo(repo),
        'Update GitHubrepository',
        onError,
      );
      return result;
    },
    onSuccess: (result) => {
      if (!result) 
        return;
      queryClient.invalidateQueries({ queryKey: ['repos'] });
    },
  });
}