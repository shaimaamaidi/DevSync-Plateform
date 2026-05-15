import { useQuery } from '@tanstack/react-query';
import type { FolderWithListsMetadata } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { clickUpStructureMetadataService } from '@/services/clickup-space-structure-metadata-service';
import { useMemo } from 'react';

export function useClickUpStructure(spaceId: string) {
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  const { data, isLoading, isFetching, isError } = useQuery<FolderWithListsMetadata[] | null>({
    queryKey: ['clickup-structure', spaceId], 
    queryFn: async () => {
      const data = await withErrorHandling(
        () => clickUpStructureMetadataService.getSpaceStructure(spaceId),
        'Load click up space structure',
        onError,
      );
      return data;
    },
    enabled: !!spaceId,  
  });

  return {
    structure: data ?? [],
    loading: isLoading,
    isFetching: isFetching,
    isStructureEmpty: data?.length === 0,
    error: isError ? 'Unable to load click up space structure' : null,
  };
}