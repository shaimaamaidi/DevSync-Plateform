import { useEffect, useState } from 'react';
import { memberService } from '@/services/member-service';
import type { MemberDTO } from '@/api/api';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import { useNavigate } from 'react-router-dom';

export function useMembers() {
  const [members, setMembers] = useState<MemberDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const onError = defaultOnError(navigate);

  useEffect(() => {
    async function fetchMembers() {
      setLoading(true);
      setError(null);

      const data = await withErrorHandling(
        () => memberService.getAllWithRepos(),
        'Load members',
        onError,
      );

      if (data) {
        const mapped: MemberDTO[] = data.map(memberService.mapToMemberDTO);
        setMembers(mapped);
      } else {
        setError('Unable to load members');
        setMembers([]);
      }

      setLoading(false);
    }

    fetchMembers();
  }, []);

  return { members, loading, error };
}