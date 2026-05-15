import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpService } from '@/services/clickup-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useDeleteClickUpSpace() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 
  
  return useMutation({
    mutationFn: async (id: number) => {
      const result = await withErrorHandling(
        () => clickUpService.deleteSpace(id),
        'Delete click up space',
        onError,
      );
      return result;
    },
    onSuccess: (result) => {
      if (!result) {
        return;
      }
      queryClient.invalidateQueries({ queryKey: ['clickup-spaces'] });
    },
  });
}