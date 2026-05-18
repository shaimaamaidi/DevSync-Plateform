import { useQuery } from '@tanstack/react-query';
import { memberService } from '@/services/member-service';
import type { MemberDTO } from '@/api/api';
import { defaultOnError } from '@/services/api-error';
import { extractStatusCode, resolveErrorAction, normalizeErrorMessage, extractErrorCode } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

export function useMembers() {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const { data, isLoading, isError } = useQuery<MemberDTO[]>({
    queryKey: ['members'],
    queryFn: async () => {
      try {
        const data = await memberService.getAllWithRepos();
        return data ? data.map(memberService.mapToMemberDTO) : [];
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
    members: data ?? [],
    loading: isLoading,
    error: isError ? 'Unable to load members' : null,
  };
}