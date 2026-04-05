import { showErrorToast } from "@/components/global-error-toaster";
import { authService } from "@/services/auth-service";
import type { NavigateFunction } from "react-router-dom";

export const defaultOnError = (navigate?: NavigateFunction) => async () => {
  await authService.logout();
  if (navigate) 
    navigate('/login');
  showErrorToast('A server error occurred. Please try again later.');
};