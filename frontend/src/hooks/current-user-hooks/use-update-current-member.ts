import { useMutation, useQueryClient } from '@tanstack/react-query';
import { memberService } from '@/services/member-service';
import { defaultOnError } from '@/services/api-error';
import { resolveErrorAction, normalizeErrorMessage, extractErrorCode, extractStatusCode } from '@/utils/error-handler';
import type { MemberUpdateDTO } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

export function useUpdateCurrentUser() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  return useMutation({
    retry: false,
    mutationFn: async (member: MemberUpdateDTO) => {
      try {
        const result = await memberService.updateMember(member);
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
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });
}