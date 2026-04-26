import type { ApiErrorType } from "./api-error-type";

export class SseError extends Error {
  public readonly status: number;
  public readonly errorType: ApiErrorType;

  constructor(
    message: string,
    status: number,
    errorType: ApiErrorType,
  ) {
    super(message);

    this.name = 'SseError';
    this.status = status;
    this.errorType = errorType;
  }
};