import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpStructureCreationService } from '@/services/clickup-workspace-creation-service';
import { extractErrorCode, handleApiError, normalizeErrorMessage } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import type { ClickUpSpaceDTO, ClickUpSpaceRegisterDTO } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

const ERROR_CODE_NOT_FOUND = 'CLICKUP_RESOURCE_NOT_FOUND';
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
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  return useMutation<RegisterSpaceResult, never, ClickUpSpaceRegisterDTO>({
    mutationFn: async (request): Promise<RegisterSpaceResult> => {
      try {
        const data = await clickUpStructureCreationService.registerSpace(request);

        if (!data) {
          return { ok: false, reason: 'handled' };
        }

        return { ok: true, data };

      } catch (err) {
        const code   = extractErrorCode(err);
        const status = (err as any)?.response?.status as number | undefined;

        if (code === ERROR_CODE_NOT_FOUND || status === 404) {
          return { ok: false, reason: 'not_found' };
        }

        if (code === ERROR_CODE_NAME_MISMATCH || status === 409) {
          return { ok: false, reason: 'name_mismatch', actualName: extractActualName(err) };
        }

        const errorType = handleApiError(err);
        const message   = normalizeErrorMessage(err);
        onError(errorType, message);

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