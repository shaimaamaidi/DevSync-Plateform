import type { ApiErrorType } from "@/types/api-error-type";

type ErrorLike = {
  message?: string;
  response?: {
    data?: unknown;
    status?: number;
  };
};

type ErrorListener = (msg: string) => void;
const listeners: ErrorListener[] = [];

export function subscribeToApiError(listener: ErrorListener) {
  listeners.push(listener);
  return () => {
    const idx = listeners.indexOf(listener);
    if (idx !== -1) listeners.splice(idx, 1);
  };
}

export const normalizeErrorMessage = (error: ErrorLike | unknown): string => {
  if (!error || typeof error !== 'object') return 'Unknown error';

  const err = error as ErrorLike;
  const responseData = err.response?.data;

  if (typeof responseData === 'string') return responseData;

  if (responseData && typeof responseData === 'object') {
    if ('detail' in responseData) {
      const detail = (responseData as { detail?: string | string[] }).detail;
      if (Array.isArray(detail)) return detail.join(', ');
      if (typeof detail === 'string') return detail;
    }
    if ('error' in responseData && typeof (responseData as any).error === 'object') {
      const errorObj = (responseData as any).error;
      if ('message' in errorObj && typeof errorObj.message === 'string') return errorObj.message;
    }
    if ('message' in responseData && typeof (responseData as { message?: string }).message === 'string') {
      return (responseData as { message?: string }).message ?? 'Unknown error';
    }
  }

  if (typeof err.message === 'string' && err.message.trim().length > 0) return err.message;

  return 'Unknown error';
};

const isAuthError = (error: ErrorLike | unknown, includeValidation = false): boolean => {
  const status = (error as ErrorLike)?.response?.status;
  if (status === 401 || status === 403) 
    return true;
  
  if (includeValidation && (status === 422 || status === 404)) 
    return true;
  return false;
};

const isServerError = (error: ErrorLike | unknown): boolean => {
  const status = (error as ErrorLike)?.response?.status;
  if (!status) 
    return true;
  if (status === 429 || status === 502) 
    return false;
  return status >= 500;
};

export const handleApiError = (
  error: ErrorLike | unknown,
  includeValidation = false,
): ApiErrorType => {
  if (isAuthError(error, includeValidation)) 
    return 'auth_error';
  if (isServerError(error)) 
    return 'server_error';
  return 'backend_error';
};

export const withErrorHandling = async <T>(
  fn: () => Promise<T>,
  context: string,
  onError?: (errorType: ApiErrorType, message: string) => void,
): Promise<T | null> => {
  try {
    return await fn();
  } catch (err) {
    const errorType = handleApiError(err);
    const message = normalizeErrorMessage(err);

    if (onError) {
      onError(errorType, message);
    }else{
      listeners.forEach((cb) => cb(`${context}: ${message}`));
    }
    return null;
  }
};