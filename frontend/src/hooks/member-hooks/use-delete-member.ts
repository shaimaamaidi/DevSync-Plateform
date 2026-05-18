import { useMutation, useQueryClient } from '@tanstack/react-query';
import { memberService } from '@/services/member-service';
import { defaultOnError } from '@/services/api-error';
import { extractStatusCode, resolveErrorAction, normalizeErrorMessage, extractErrorCode } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

export function useDeleteMember() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  return useMutation({
    mutationFn: async (id: number) => {
      try {
        const result = await memberService.deleteMember(id);
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
    onSuccess: (result) => {
      if (!result) 
        return;
      queryClient.invalidateQueries({ queryKey: ['members'] });
    },
  });
}