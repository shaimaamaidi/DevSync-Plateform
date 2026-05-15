import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpService } from '@/services/clickup-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import type { ClickUpSpaceUpdateDTO } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useUpdateClickUpSpace() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 
  
  return useMutation({
    mutationFn: async (space: ClickUpSpaceUpdateDTO) => {
      const result = await withErrorHandling(
        () => clickUpService.updateSpace(space),
        'Update click up space',
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