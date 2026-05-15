import { useQuery } from '@tanstack/react-query';
import { memberService } from '@/services/member-service';
import type { MemberDTO } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useMembers() {
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  const { data, isLoading, isError } = useQuery<MemberDTO[] | null>({
    queryKey: ['members'],
    queryFn: async () => {
      const data = await withErrorHandling(
        () => memberService.getAllWithRepos(),
        'Load members',
        onError,
      );
      if (!data) 
        return null;
      return data.map(memberService.mapToMemberDTO); 
    },
  });

  return {
    members: data ?? [],
    loading: isLoading,
    error: isError ? 'Unable to load members' : null,
  };
}