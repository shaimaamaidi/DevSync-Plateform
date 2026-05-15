import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpStructureCreationService } from '@/services/clickup-workspace-creation-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import type { CreateListRequest, ClickUpListMetadata } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useCreateList(spaceId: string) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  return useMutation<ClickUpListMetadata | null, Error, CreateListRequest>({
    mutationFn: async (request) => {
      const result = await withErrorHandling(
        () => clickUpStructureCreationService.createList(request),
        'Create click up list',
        onError,
      );

      return result;
    },
    onSuccess: (result) => {
      if (!result) {
        return;
      }
      queryClient.invalidateQueries({ queryKey: ['clickup-structure', spaceId] });
    },
  });
}