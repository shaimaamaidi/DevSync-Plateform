import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpStructureCreationService } from '@/services/clickup-workspace-creation-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import type { CreateFolderRequest, FolderWithListsMetadata } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useCreateFolder(spaceId: string) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  return useMutation<FolderWithListsMetadata | null, Error, CreateFolderRequest>({
    mutationFn: async (request) => {
      const result = await withErrorHandling(
        () => clickUpStructureCreationService.createFolder(request),
        'Create click upfolder',
        onError,
      );

      return result;
    },
    onSuccess: (result) => {
      if (!result) {
        return;
      }
      queryClient.invalidateQueries({ queryKey: ['clickup-structure', spaceId] });
    },
  });
}