type ErrorLike = {
  message?: string;
  response?: {
    data?: unknown;
    status?: number;
  };
};

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
  alert(`${context}: ${message}`);
};
