import { useQuery } from '@tanstack/react-query';
import { authService } from '@/services/auth-service';
import type { MemberDTO } from '@/api/api';
import { defaultOnError } from '@/services/api-error';
import { resolveErrorAction, normalizeErrorMessage, extractErrorCode, extractStatusCode } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

export function useCurrentUser() {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const { data, isLoading, isError } = useQuery<MemberDTO | null>({
    queryKey: ['currentUser'],
    retry: false,
    queryFn: async () => {
      try {
        const result = await authService.getMe();
        return result ;
      } catch (err) {
        const action  = resolveErrorAction(err);
        const message = normalizeErrorMessage(err);
        const code    = extractErrorCode(err);
        const status  = extractStatusCode(err);

        await onError()(action, message, { code, status: status ?? undefined });

        throw err;
      }
    },
  });

  return {
    user: data ?? null,
    loading: isLoading,
    error: isError ? 'Unable to load user' : null,
  };
}