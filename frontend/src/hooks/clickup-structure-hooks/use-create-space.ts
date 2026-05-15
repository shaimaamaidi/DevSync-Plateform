import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpStructureCreationService } from '@/services/clickup-workspace-creation-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import type { CreateSpaceRequest, ClickUpSpaceDTO } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useCreateClickUpSpace() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  return useMutation<ClickUpSpaceDTO | null, Error, CreateSpaceRequest>({
    mutationFn: async (request) => {
      const result = await withErrorHandling(
        () => clickUpStructureCreationService.createSpace(request),
        'Create click up space',
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