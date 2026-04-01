import { Navigate, useLocation } from 'react-router-dom';
import { authService } from '@/services/auth-service';
import type { JSX } from 'react/jsx-runtime';

export function RequireAuth({ children }: { children: JSX.Element }) {
  const location = useLocation();
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}
