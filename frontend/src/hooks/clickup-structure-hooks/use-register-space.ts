import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpStructureManagementService } from '@/services/clickup-workspace-management-service';
import { defaultOnError } from '@/services/api-error';
import { extractStatusCode, resolveErrorAction, normalizeErrorMessage, extractErrorCode } from '@/utils/error-handler';
import type { ClickUpSpaceDTO, ClickUpSpaceRegisterDTO } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

const ERROR_CODE_NOT_FOUND    = 'CLICKUP_RESOURCE_NOT_FOUND';
const ERROR_CODE_NAME_MISMATCH = 'CLICKUP_SPACE_NAME_MISMATCH';

export type RegisterSpaceResult =
  | { ok: true;  data: ClickUpSpaceDTO }
  | { ok: false; reason: 'not_found' }
  | { ok: false; reason: 'name_mismatch'; actualName: string | null }
  | { ok: false; reason: 'handled' };

const extractActualName = (err: unknown): string | null => {
  try {
    const detail: string = (err as any)?.response?.data?.detail ?? '';
    return detail.match(/got '(.+?)'/)?.[1] ?? null;
  } catch {
    return null;
  }
};

export function useRegisterClickUpSpace() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  return useMutation<RegisterSpaceResult, never, ClickUpSpaceRegisterDTO>({
    mutationFn: async (request): Promise<RegisterSpaceResult> => {
      try {
        const data = await clickUpStructureManagementService.registerSpace(request);

        if (!data) return { ok: false, reason: 'handled' };

        return { ok: true, data };

      } catch (err) {
        const code   = extractErrorCode(err);
        const status = extractStatusCode(err);  

        if (code === ERROR_CODE_NOT_FOUND || status === 404) {
          return { ok: false, reason: 'not_found' };
        }

        if (code === ERROR_CODE_NAME_MISMATCH || status === 409) {
          return { ok: false, reason: 'name_mismatch', actualName: extractActualName(err) };
        }

        const action  = resolveErrorAction(err);
        const message = normalizeErrorMessage(err);

        await onError()(action, message, { code, status: status ?? undefined });

        return { ok: false, reason: 'handled' };
      }
    },

    onSuccess: (result) => {
      if (result.ok) {
        queryClient.invalidateQueries({ queryKey: ['clickup-spaces'] });
      }
    },
  });
}