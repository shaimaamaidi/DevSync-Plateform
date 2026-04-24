export interface StreamResult {
  threadId: string | null;
  text: string;
  json: unknown;
}

export async function readSseStream(
  stream: ReadableStream<Uint8Array>,
  onChunk?: (chunk: string) => void,
): Promise<StreamResult> {
  const reader  = stream.getReader();
  const decoder = new TextDecoder();
  let buffer    = "";
  let threadId: string | null = null;
  const textChunks: string[]  = [];

  const consumeFrame = (frame: string) => {
    const lines = frame
      .split("\n")
      .filter((l) => l.startsWith("data:"))
      .map((l) => l.slice(5).trim())
      .filter(Boolean);

    for (const line of lines) {
      try {
        const payload = JSON.parse(line);
        if (payload?.thread_id) threadId = payload.thread_id;
        if (typeof payload?.text === "string") {
          textChunks.push(payload.text);
          onChunk?.(payload.text);
        }
      } catch { /* ignore */ }
    }
  };

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

  if (buffer.trim()) consumeFrame(buffer);

  const rawText = textChunks.join("").trim();
  const { text, json } = parseResponse(rawText);
  return { threadId, text, json };
}

function parseResponse(raw: string): { text: string; json: unknown } {
  const tryParseJson = (input: string): unknown => {
    const trimmed = (input ?? "").trim();
    if (!trimmed) return null;
    try { return JSON.parse(trimmed); } catch { /* continue */ }
    const start = Math.min(
      ...[trimmed.indexOf("{"), trimmed.indexOf("[")].filter((idx) => idx >= 0),
    );
    if (!Number.isFinite(start)) return null;
    const open = trimmed[start] as "{" | "[";
    const close = open === "{" ? "}" : "]";
    let depth = 0, inString = false, escaped = false;
    for (let i = start; i < trimmed.length; i++) {
      const ch = trimmed[i];
      if (inString) {
        if (escaped) escaped = false;
        else if (ch === "\\") escaped = true;
        else if (ch === '"') inString = false;
        continue;
      }
      if (ch === '"') { inString = true; continue; }
      if (ch === open) depth++;
      if (ch === close) {
        depth--;
        if (depth === 0) {
          try { return JSON.parse(trimmed.slice(start, i + 1)); } catch { return null; }
        }
      }
    }
    return null;
  };

  const fencedJsonRegex = /```(?:json)?\s*([\s\S]*?)```/gi;
  const fencedMatches = Array.from(raw.matchAll(fencedJsonRegex));
  const text = raw.replace(/```(?:json)?[\s\S]*?```/gi, "").trim();
  let json: unknown = null;
  for (const match of fencedMatches) {
    const parsed = tryParseJson(match[1]);
    if (parsed !== null) { json = parsed; break; }
  }
  if (json === null) json = tryParseJson(raw);
  return { text, json };
}
