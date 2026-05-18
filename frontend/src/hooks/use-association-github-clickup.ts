import { useMutation, useQueryClient } from '@tanstack/react-query';
import { defaultOnError } from '@/services/api-error';
import { resolveErrorAction, normalizeErrorMessage, extractErrorCode, extractStatusCode } from '@/utils/error-handler';
import type { AssociateClickUpSpaceRequest } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';
import { gitHubClickUpAssociationService } from '@/services/github-clickup-association-service';

export function useAssociateRepoWithClickUpSpace() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  return useMutation({
    retry: false,
    mutationFn: async (association: AssociateClickUpSpaceRequest) => {
      try {
        return await gitHubClickUpAssociationService.associateRepoWithClickUp(association);
      } catch (err) {
        const action = resolveErrorAction(err);
        const message = normalizeErrorMessage(err);
        const code = extractErrorCode(err);
        const status = extractStatusCode(err);
        await onError()(action, message, { code, status: status ?? undefined });
        throw err;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repos'] });
      queryClient.invalidateQueries({ queryKey: ['clickup-spaces'] });
    },
  });
}