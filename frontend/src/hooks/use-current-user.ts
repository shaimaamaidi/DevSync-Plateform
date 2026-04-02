import { useEffect, useState } from 'react';
import { memberService } from '@/services/member-service';
import type { MemberWithReposDTO } from '@/api/api';

export function useCurrentUser() {
  const [user, setUser] = useState<MemberWithReposDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function fetchUser() {
      setLoading(true);
      setError(null);
      try {
        const members = await memberService.getAllWithRepos();
        if (members.length > 0) {
          setUser(members[0]);
        } else {
          setUser(null);
        }
      } catch (err: any) {
        setError('Unable to load user');
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    fetchUser();
    return () => { mounted = false; };
  }, []);

  return { user, loading, error };
}
