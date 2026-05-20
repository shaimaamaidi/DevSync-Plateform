import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clickUpStructureManagementService } from '@/services/clickup-workspace-management-service';
import { extractErrorCode, extractStatusCode, normalizeErrorMessage, resolveErrorAction } from '@/utils/error-handler';
import type { CreateFolderRequest, FolderWithListsMetadata } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';
import { defaultOnError } from '@/services/api-error';

export function useCreateFolder(spaceId: string) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useCallback(() => defaultOnError(navigate), [navigate]);

  return useMutation<FolderWithListsMetadata | null, Error, CreateFolderRequest>({
    mutationFn: async (request) => {
      try {
        const result = await clickUpStructureManagementService.createFolder(request);
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
      if (!result) {
        return;
      }
      queryClient.invalidateQueries({ queryKey: ['clickup-structure', spaceId] });
    },
  });
}