import { useQuery } from '@tanstack/react-query';
import { clickUpService } from '@/services/clickup-service';
import type { RepoClickUpSpaceDTO } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useClickUpSpacesList() {
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  const { data, isLoading, isError } = useQuery<RepoClickUpSpaceDTO[] | null>({
    queryKey: ['clickup-spaces'],
    queryFn: async () => {
      const data = await withErrorHandling(
        () => clickUpService.getAllSpaces(),
        'Load ClickUp spaces',
        onError,
      );

      return data;
    },
  });

  return {
    spaces: data ?? [],
    loading: isLoading,
    error: isError ? 'Unable to load ClickUp spaces' : null,
  };
}