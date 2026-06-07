import { useCurrentUser } from '@/hooks/current-user-hooks/use-current-user';
import { Navigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import type { JSX } from 'react';

export function RequireAdminRoute({ children }: { children: JSX.Element }) {
  const { user, loading } = useCurrentUser();

  if (loading) return (
    <div className="flex items-center justify-center h-full py-24">
      <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
    </div>
  );

  if (user?.role !== 'admin') return <Navigate to="/repositories" replace />;

  return children;
}