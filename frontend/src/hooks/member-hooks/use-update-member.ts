import { useMutation, useQueryClient } from '@tanstack/react-query';
import { memberService } from '@/services/member-service';
import { withErrorHandling } from '@/services/api-error';
import { defaultOnError } from '@/lib/error-utils';
import type { MemberUpdateDTO } from '@/api/api';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

export function useUpdateMember() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const onError = useMemo(() => defaultOnError(navigate), [navigate]); 

  return useMutation({
    mutationFn: async (member: MemberUpdateDTO) => {
      const result = await withErrorHandling(
        () => memberService.updateMember(member),
        'Update member',
        onError,
      );
      return result;
    },
    onSuccess: (result) => {
      if (!result) 
        return;
      queryClient.invalidateQueries({ queryKey: ['members'] });
    },
  });
}