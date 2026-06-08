import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { onAxiosError } from "@/api/axios-interceptor";
import { defaultOnError } from "@/services/api-error";
import type { ErrorAction } from "@/types/api-error-type";

export function AxiosErrorBoundary() {
  const navigate = useNavigate();

  useEffect(() => {
    const onError = defaultOnError(navigate);

    const unsub = onAxiosError(({ action, message, code, status }) => {
      onError(action as ErrorAction, message, { code, status });
    });

    return unsub;
  }, [navigate]);

  return null;
}