import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpService } from '@/services/clickup-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import type { ClickUpSpaceCreateDTO } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useAddClickUpSpace() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  return useMutation({
    mutationFn: async (newSpace: ClickUpSpaceCreateDTO) => {
      const result = await withErrorHandling(
        () => clickUpService.createSpace(newSpace),
        'Create clickup space',
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