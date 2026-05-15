import { useMutation, useQueryClient } from '@tanstack/react-query';
import { repoService } from '@/services/repo-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useDeleteRepo() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  return useMutation({
    mutationFn: async (id: number) => {
      const result = await withErrorHandling(
        () => repoService.deleteRepo(id),
        'Delete GitHub repository',
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