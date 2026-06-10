import { emitAxiosErrorNetworkOnly, type AxiosErrorEvent } from '@/api/axios-interceptor';
import { resolveErrorAction } from './error-handler';

export interface StreamResult {
  threadId: string | null;
  text: string;
  json: unknown;
  invalidDescription?: { message: string } | null;
  backlogPreview?: string | null;
  deliveryPlanPreview?: string | null;
}

class SseBusinessError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'SseBusinessError';
  }
}

export async function readSseStream(
  stream: ReadableStream<Uint8Array>,
  onChunk?: (chunk: string) => void,
  onToolCall?: (name: string) => void,
  onInvalidDescription?: (message: string) => void,
): Promise<StreamResult> {
  const reader  = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let threadId: string | null = null;
  const textChunks: string[]  = [];
  let invalidDescription: { message: string } | null = null;
  let backlogPreview: string | null = null;
  let deliveryPlanPreview: string | null = null;

  const consumeFrame = (frame: string) => {
    const lines = frame
      .split("\n")
      .filter((l) => l.startsWith("data:"))
      .map((l) => l.slice(5).trim())
      .filter(Boolean);

    for (const line of lines) {
      try {
        const payload = JSON.parse(line);
        if (payload?.error) {
          const code: string | null = payload.error?.code ?? null;
          const message: string =
            payload.error?.message ?? 'Stream error occurred';
          const status: number | undefined = payload.error?.status;

          const errorLike = { response: { status, data: { error: { code, message } } } };
          const action = resolveErrorAction(errorLike);

          const emitAction: AxiosErrorEvent["action"] | null = action === 'SILENT' ? null : action as AxiosErrorEvent["action"];

          if (emitAction) {
            emitAxiosErrorNetworkOnly({ action: emitAction as AxiosErrorEvent["action"], message, code, status });
          }

          throw new SseBusinessError(message);
        }

        if (payload?.thread_id) threadId = payload.thread_id;

        if (payload?.tool_call?.name) {
          onToolCall?.(payload.tool_call.name);
        }
        
        if (typeof payload?.backlog_preview === 'string') {
          backlogPreview = payload.backlog_preview;
        }

        if (typeof payload?.delivery_plan_preview === 'string') {
          deliveryPlanPreview = payload.delivery_plan_preview;
        }

        if (typeof payload?.text === 'string') {
          textChunks.push(payload.text);
          onChunk?.(payload.text);
        }

        if (
          (payload?.invalid_description === true && payload?.message) ||
          (payload?.status === "invalid" && payload?.message)
        ) {
          invalidDescription = { message: payload.message };
          onInvalidDescription?.(payload.message);
        }
      } catch (err) {
        if (err instanceof SseBusinessError) {
          throw err;
        }
        // Silently ignore malformed SSE lines.
      }
    }
  };

  try {
    while (true) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      let boundary = buffer.indexOf("\n\n");
      while (boundary !== -1) {
        consumeFrame(buffer.slice(0, boundary));
        buffer = buffer.slice(boundary + 2);
        boundary = buffer.indexOf("\n\n");
      }
      if (done) break;
    }
  } catch (err) {
    if (err instanceof SseBusinessError) {
      throw err;
    }

    if (err instanceof Error) {
      const isAlreadyEmitted = err.message === 'Session expired. Redirecting to login.';
      if (!isAlreadyEmitted) {
        const isNetworkError =
          err instanceof TypeError &&
          (err.message === 'Failed to fetch' || err.message === 'Network Error');

        const errorLike = { response: { status: 503, data: { error: { code: 'STREAM_EXECUTION_ERROR', message: err.message || 'Stream connection lost' } } } };
        const action = resolveErrorAction(errorLike);
        emitAxiosErrorNetworkOnly({
          action: isNetworkError ? 'NETWORK_DOWN' : action as AxiosErrorEvent["action"],
          message: err.message || 'Stream connection lost',
          code: isNetworkError ? null : 'STREAM_EXECUTION_ERROR',
        });
      }
    }
    throw err;
  } finally {
    try { reader.releaseLock(); } catch { /* ignore */ }
  }

  if (buffer.trim()) consumeFrame(buffer);

  const rawText = textChunks.join("").trim();
  const { text, json } = parseResponse(rawText);
  return { threadId, text, json, invalidDescription, backlogPreview, deliveryPlanPreview  };
}

function parseResponse(raw: string): { text: string; json: unknown } {
  const tryParseJson = (input: string): unknown => {
    const trimmed = (input ?? "").trim();
    if (!trimmed) return null;
    try { return JSON.parse(trimmed); } catch { /* continue */ }

    for (let start = 0; start < trimmed.length; start++) {
      const ch = trimmed[start];
      if (ch !== "{" && ch !== "[") continue;
      const close = ch === "{" ? "}" : "]";
      let depth = 0, inString = false, escaped = false;
      for (let i = start; i < trimmed.length; i++) {
        const c = trimmed[i];
        if (inString) {
          if (escaped) escaped = false;
          else if (c === "\\") escaped = true;
          else if (c === '"') inString = false;
          continue;
        }
        if (c === '"') { inString = true; continue; }
        if (c === ch) depth++;
        if (c === close) {
          depth--;
          if (depth === 0) {
            try {
              const parsed = JSON.parse(trimmed.slice(start, i + 1));
              return parsed;
            } catch { break; }
          }
        }
      }
    }
    return null;
  };

  // Manual fenced block extraction
  const fenceStart = raw.indexOf("```");
  if (fenceStart !== -1) {
    const afterFence = raw.indexOf("\n", fenceStart);
    const fenceEnd = raw.indexOf("```", afterFence);
    if (afterFence !== -1 && fenceEnd !== -1) {
      const inside = raw.slice(afterFence + 1, fenceEnd).trim();
      const parsed = tryParseJson(inside);
      if (parsed !== null) {
        const textBefore = raw.slice(0, fenceStart).trim();
        return { text: textBefore, json: parsed };
      }
    }
  }

  // Regex fenced fallback
  const fencedJsonRegex = /```(?:json)?\s*([\s\S]*?)```/gi;
  const fencedMatches = Array.from(raw.matchAll(fencedJsonRegex));
  for (const match of fencedMatches) {
    const parsed = tryParseJson(match[1]);
    if (parsed !== null) {
      const textWithoutFences = raw.replace(/```(?:json)?[\s\S]*?```/gi, "").trim();
      return { text: textWithoutFences, json: parsed };
    }
  }

  // Pure JSON
  try {
    const parsed = JSON.parse(raw.trim());
    return { text: "", json: parsed };
  } catch { /* continue */ }

  // Embedded JSON
  const extracted = tryParseJson(raw);
  if (extracted !== null) {
    const jsonStart = Math.min(
      ...[raw.indexOf("{"), raw.indexOf("[")].filter((i) => i >= 0),
    );
    const narrativeText = Number.isFinite(jsonStart)
      ? raw.slice(0, jsonStart).trim()
      : raw.trim();
    return { text: narrativeText, json: extracted };
  }

  return { text: raw.trim(), json: null };
}