import { useQuery } from '@tanstack/react-query';
import { clickupSpaceTaskReaderService } from '@/services/clickup-space-task-reader';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';
import type { FolderWithLists } from '@/api/api';

export function useSpaceTasks(spaceId: string) {
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]);

  const { data, isLoading, isError } = useQuery<FolderWithLists[] | null>({
    queryKey: ['space-tasks', spaceId],
    queryFn: async () => {
      const result = await withErrorHandling(
        () => clickupSpaceTaskReaderService.getTasksBySpace(spaceId),
        'Load click up space tasks',
        onError,
      );
      return result;
    },
    enabled: !!spaceId,
  });

  return {
    folders: data ?? [],
    loading: isLoading,
    error: isError ? 'Unable to load tasks for this space.' : null,
  };
}