import { useQuery } from '@tanstack/react-query';
import { authService } from '@/services/auth-service';
import type { MemberDTO } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useCurrentUser() {
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  const { data, isLoading, isError } = useQuery<MemberDTO | null>({
    queryKey: ['currentUser'],
    queryFn: async () =>
      withErrorHandling(
        () => authService.getMe(),
        'Load current user',
        onError,
      ) ?? null,
  });

  return {
    user: data ?? null,
    loading: isLoading,
    error: isError ? 'Unable to load user' : null,
  };
}