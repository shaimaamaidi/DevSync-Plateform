import { useMutation, useQueryClient } from '@tanstack/react-query';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import type { AssociateClickUpSpaceRequest } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';
import { gitHubClickUpAssociationService } from '@/services/github-clickup-association-service';

export function useAssociateRepoWithClickUpSpace() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  return useMutation({
    mutationFn: async (association: AssociateClickUpSpaceRequest) => {
      const result = await withErrorHandling(
        () => gitHubClickUpAssociationService.associateRepoWithClickUp(association),
        'Associate GitHub repository with ClickUp space',
        onError,
      );
      return result;
    },
    onSuccess: (result) => {
      if (!result) 
        return;
      queryClient.invalidateQueries({ queryKey: ['repos'] });
      queryClient.invalidateQueries({ queryKey: ['clickup-spaces'] });
    },
  });
}