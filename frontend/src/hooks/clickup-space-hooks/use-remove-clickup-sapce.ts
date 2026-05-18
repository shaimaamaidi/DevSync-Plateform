import { useMutation, useQueryClient } from '@tanstack/react-query';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';
import { clickUpStructureCreationService } from '@/services/clickup-workspace-creation-service';

export function useRemoveClickUpSpace() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  return useMutation({
    mutationFn: async (spaceId: number) => {
      const result = await withErrorHandling(
        () => clickUpStructureCreationService.deleteSpace(spaceId),
        'Remove click up space',
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