import type { ApiErrorPayload, DecodeRunResponse, DecodeRunStatus } from '../types/api';

const DEFAULT_BASE_URL = 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly errorCode: string,
  ) {
    super(message);
  }
}

function getBaseUrl(): string {
  const envUrl = (import.meta as ImportMeta & { env?: { WXT_BACKEND_URL?: string } }).env
    ?.WXT_BACKEND_URL;
  return typeof envUrl === 'string' && envUrl.length > 0 ? envUrl : DEFAULT_BASE_URL;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getBaseUrl()}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as ApiErrorPayload | null;
    throw new ApiError(
      payload?.message ?? 'Unexpected API error',
      response.status,
      payload?.error_code ?? 'unknown_error',
    );
  }

  return (await response.json()) as T;
}

export function decodeBrief(text: string): Promise<DecodeRunResponse> {
  return request<DecodeRunResponse>('/v1/briefs/decode', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export function getRunStatus(runId: string): Promise<DecodeRunStatus> {
  return request<DecodeRunStatus>(`/v1/briefs/runs/${runId}`);
}
