import { showErrorToast } from "@/components/global-error-toaster";
import type { ApiErrorType } from "@/services/api-error";
import { authService } from "@/services/auth-service";
import type { NavigateFunction } from "react-router-dom";

export const defaultOnError = (navigate?: NavigateFunction) => async (errorType: ApiErrorType, message: string) => {
  if (errorType === 'backend_error') {
    showErrorToast(message, 'Operation failed');
    return;
  }
  await authService.logout();
  if (navigate) 
    navigate('/login');
  showErrorToast('A server error occurred. Please try again later.');
};