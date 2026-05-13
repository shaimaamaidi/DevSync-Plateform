import { useMutation, useQueryClient } from '@tanstack/react-query';
import { repoService } from '@/services/repo-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import type { GitRepoCreateDTO } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useAddRepo() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  return useMutation({
    mutationFn: async (newRepo: GitRepoCreateDTO) => {
      const result = await withErrorHandling(
        () => repoService.createRepo(newRepo),
        'Create GitHub repository',
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