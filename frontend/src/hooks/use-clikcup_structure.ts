import { useEffect, useState } from 'react';
import type { FolderWithListsMetadata } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import { useNavigate } from 'react-router-dom';
import { clickUpStructureMetadataService } from '@/services/clickup-space-structure-metadata-service';

export function useClickUpStructure(spaceId: string) {
  const [structure, setStructure] = useState<FolderWithListsMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const onError = defaultOnError(navigate);

  useEffect(() => {
    async function fetchStructure() {
      setLoading(true);
      setError(null);

      const data = await withErrorHandling(
        () => clickUpStructureMetadataService.getSpaceStructure(spaceId),
        'Load ClickUp space structure',
        onError,
      );

      if (data) {
        setStructure(data);
      } else {
        setError('Unable to load ClickUp space structure');
        setStructure([]);
      }
      setLoading(false);
    }
    fetchStructure();
  }, [spaceId]);

  return { structure, loading, error };
}