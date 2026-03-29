type ErrorLike = {
  message?: string;
  response?: {
    data?: unknown;
    status?: number;
  };
};

// Simple event system to broadcast errors to a UI alert handler
type ErrorListener = (msg: string) => void;
const listeners: ErrorListener[] = [];
export function subscribeToApiError(listener: ErrorListener) {
  listeners.push(listener);
  return () => {
    const idx = listeners.indexOf(listener);
    if (idx !== -1) listeners.splice(idx, 1);
  };
}

const normalizeErrorMessage = (error: ErrorLike | unknown): string => {
  if (!error || typeof error !== 'object') {
    return 'Unknown error';
  }

  const err = error as ErrorLike;
  const responseData = err.response?.data;

  if (typeof responseData === 'string') {
    return responseData;
  }


  if (responseData && typeof responseData === 'object') {
    if ('detail' in responseData) {
      const detail = (responseData as { detail?: string | string[] }).detail;
      if (Array.isArray(detail)) {
        return detail.join(', ');
      }
      if (typeof detail === 'string') {
        return detail;
      }
    }

    // Support backend error format: { error: { message: ... } }
    if ('error' in responseData && typeof (responseData as any).error === 'object') {
      const errorObj = (responseData as any).error;
      if ('message' in errorObj && typeof errorObj.message === 'string') {
        return errorObj.message;
      }
    }

    if ('message' in responseData && typeof (responseData as { message?: string }).message === 'string') {
      return (responseData as { message?: string }).message ?? 'Unknown error';
    }
  }

  if (typeof err.message === 'string' && err.message.trim().length > 0) {
    return err.message;
  }

  return 'Unknown error';
};

export const handleApiError = (error: ErrorLike | unknown, context: string) => {
  const message = normalizeErrorMessage(error);
  listeners.forEach((cb) => cb(`${context}: ${message}`));
};
