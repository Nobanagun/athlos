import { getApiUrl } from "@/shared/env";

/**
 * Thin fetch wrapper: base URL, Authorization header, centralized 401
 * handling. No new dependency (axios, ky, ...) - fetch is already
 * available in React Native/Expo (see docs/DECISIONS.md: same
 * minimalism criterion already applied on the backend).
 */

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * True for a failed HTTP response (`ApiError`) or a network-level
 * failure (`fetch` itself rejecting, surfaced as `TypeError` in both
 * React Native and browser fetch implementations) - the two failure
 * modes callers may reasonably want to tolerate for a non-critical
 * request. Deliberately excludes anything else (bugs, unexpected
 * exceptions), which should keep propagating.
 */
export function isNetworkOrApiError(error: unknown): boolean {
  return error instanceof ApiError || error instanceof TypeError;
}

type UnauthorizedHandler = () => void;

let unauthorizedHandler: UnauthorizedHandler | null = null;

/**
 * Registered once by AuthContext at startup - lets the HTTP layer react
 * to a 401 (force logout) without importing AuthContext directly and
 * creating a circular dependency.
 */
export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
  unauthorizedHandler = handler;
}

interface RequestOptions {
  method?: "GET" | "POST" | "DELETE";
  body?: unknown;
  token?: string | null;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, token } = options;

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${getApiUrl()}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401) {
    unauthorizedHandler?.();
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail =
      payload && typeof payload.detail === "string" ? payload.detail : response.statusText;
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
