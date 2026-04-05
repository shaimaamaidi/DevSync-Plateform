import { useEffect, useState } from 'react';
import { memberService } from '@/services/member-service';
import type { MemberWithReposDTO } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/utils/default-on-error';
import { useNavigate } from 'react-router-dom';

export function useCurrentUser() {
  const [user, setUser] = useState<MemberWithReposDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchUser() {
      setLoading(true);
      setError(null);
      
      const members = await withErrorHandling(
        () => memberService.getAllWithRepos(),
        'Load current user',
        defaultOnError(navigate),
      );

      if (members && members.length > 0) {
        setUser(members[0]);
      } else {
        setError('Unable to load user');
        setUser(null);
      }
      setLoading(false);
    }
    fetchUser();
  }, []);

  return { user, loading, error };
}
