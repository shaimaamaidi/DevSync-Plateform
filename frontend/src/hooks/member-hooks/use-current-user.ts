import { useQuery } from '@tanstack/react-query';
import { memberService } from '@/services/member-service';
import type { MemberWithReposDTO } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useCurrentUser() {
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  const { data, isLoading, isError } = useQuery<MemberWithReposDTO | null>({
    queryKey: ['members'], 
    queryFn: async () => {
      const members = await withErrorHandling(
        () => memberService.getAllWithRepos(),
        'Load current user',
        onError,
      );
      if (!members || members.length === 0) 
        return null;
      return members[0];
    },
  });

  return {
    user: data ?? null,
    loading: isLoading,
    error: isError ? 'Unable to load user' : null,
  };
}