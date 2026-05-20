import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpStructureManagementService } from '@/services/clickup-workspace-management-service';
import { defaultOnError } from '@/services/api-error';
import { resolveErrorAction, normalizeErrorMessage, extractErrorCode, extractStatusCode } from '@/utils/error-handler';
import type { AddStatusRequest, ClickUpListMetadata } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

export function useAddStatus(spaceId: string) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  return useMutation<ClickUpListMetadata, Error, AddStatusRequest>({
    retry: false,
    mutationFn: async (request: AddStatusRequest) => {
      try {
        const result = await clickUpStructureManagementService.addStatus(request);

        if (!result) {
          throw new Error('Failed to add status');
        }

        return result;
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
      queryClient.invalidateQueries({ queryKey: ['clickup-structure', spaceId] });
    },
  });
}