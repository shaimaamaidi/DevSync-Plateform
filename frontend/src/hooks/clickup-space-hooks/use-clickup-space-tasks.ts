import { useQuery } from '@tanstack/react-query';
import { clickupSpaceTaskReaderService } from '@/services/clickup-space-task-reader';
import { defaultOnError } from '@/services/api-error';
import { resolveErrorAction, normalizeErrorMessage, extractErrorCode, extractStatusCode } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';
import type { FolderWithLists } from '@/api/api';

export function useSpaceTasks(spaceId: string) {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const { data, isLoading, isError } = useQuery<FolderWithLists[]>({
    queryKey: ['space-tasks', spaceId],
    retry: false,
    enabled: !!spaceId,
    queryFn: async () => {
      try {
        const result = await clickupSpaceTaskReaderService.getTasksBySpace(spaceId);
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
    folders: data ?? [],
    loading: isLoading,
    error: isError ? 'Unable to load tasks for this space.' : null,
  };
}