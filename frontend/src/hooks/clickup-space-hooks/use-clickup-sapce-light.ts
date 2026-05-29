import { useQuery } from '@tanstack/react-query';
import { clickUpService } from '@/services/clickup-service';
import type { ClickUpSpaceLightDTO } from '@/api/api';
import { defaultOnError } from '@/services/api-error';
import { resolveErrorAction, normalizeErrorMessage, extractErrorCode, extractStatusCode } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

export function useClickUpSpacesLight() {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const { data, isLoading, isError, refetch } = useQuery<ClickUpSpaceLightDTO[]>({
    queryKey: ['clickup-spaces-light'],
    retry: false,
    queryFn: async () => {
      try {
        const result = await clickUpService.getAllSpacesLight();
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
  });

  return {
    spaces: data ?? [],
    loading: isLoading,
    error: isError ? 'Unable to load click up spaces' : null,
    refetch,
  };
}