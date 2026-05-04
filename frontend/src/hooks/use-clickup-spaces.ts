import { useEffect, useState } from 'react';
import { clickUpService } from '@/services/clickup-service';
import type { RepoClickUpSpaceDTO } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import { useNavigate } from 'react-router-dom';

export function useClickUpSpacesList() {
  const [spaces, setSpaces] = useState<RepoClickUpSpaceDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const onError = defaultOnError(navigate);

  useEffect(() => {
    async function fetchSpaces() {
      setLoading(true);
      setError(null);

      const data = await withErrorHandling(
        () => clickUpService.getAllSpaces(),
        'Load ClickUp spaces',
        onError,
      );

      if (data) {
        setSpaces(data);
      } else {
        setError('Unable to load ClickUp spaces');
        setSpaces([]);
      }
      setLoading(false);
    }
    fetchSpaces();
  }, []);

  return { spaces, loading, error };
}