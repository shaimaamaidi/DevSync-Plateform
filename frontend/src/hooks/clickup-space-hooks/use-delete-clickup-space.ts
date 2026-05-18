import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpService } from '@/services/clickup-service';
import { defaultOnError } from '@/services/api-error';
import { resolveErrorAction, normalizeErrorMessage, extractErrorCode, extractStatusCode } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

export function useDeleteClickUpSpace() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  return useMutation({
    retry: false,
    mutationFn: async (id: number) => {
      try {
        const result = await clickUpService.deleteSpace(id);
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
      queryClient.invalidateQueries({ queryKey: ['clickup-spaces'] });
    },
  });
}