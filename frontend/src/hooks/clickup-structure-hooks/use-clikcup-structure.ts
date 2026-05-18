import { useQuery } from '@tanstack/react-query';
import type { FolderWithListsMetadata } from '@/api/api';
import { defaultOnError } from '@/services/api-error';
import { resolveErrorAction, normalizeErrorMessage, extractErrorCode, extractStatusCode } from '@/utils/error-handler';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';
import { clickUpStructureMetadataService } from '@/services/clickup-space-structure-metadata-service';

export function useClickUpStructure(spaceId: string) {
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  const { data, isLoading, isFetching, isError } = useQuery<FolderWithListsMetadata[]>({
    queryKey: ['clickup-structure', spaceId],
    retry: false,
    enabled: !!spaceId,
    queryFn: async () => {
      try {
        const result = await clickUpStructureMetadataService.getSpaceStructure(spaceId);
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
    structure: data ?? [],
    loading: isLoading,
    isFetching,
    isStructureEmpty: !data || data.length === 0,
    error: isError ? 'Unable to load click up space structure' : null,
  };
}