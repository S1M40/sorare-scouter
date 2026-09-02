/**
 * Transport layer.
 *
 * Today every read is served by the mock implementation in
 * `src/services/mock`. When the FastAPI backend exists, set
 * `VITE_API_BASE_URL` and swap `scoutlabApi` in `src/services/api/index.ts`
 * for `createRestApi(http)` — the `ScoutlabApi` interface stays identical, so
 * no component changes are needed.
 */
export const API_BASE_URL = import.meta.env["VITE_API_BASE_URL"] ?? "";

export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === "true" || (!API_BASE_URL && import.meta.env.DEV);

/** Simulated network latency for the mock layer, keeps loading states honest. */
export function latency<T>(value: T, ms = 220): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}

// ---------------------------------------------------------------------------
// Auth token helpers (persisted in localStorage for demo convenience)
// ---------------------------------------------------------------------------

const TOKEN_KEY = "scoutlab_auth_token";

export function setAuthToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getAuthToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function clearAuthToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// ---------------------------------------------------------------------------
// HTTP transport
// ---------------------------------------------------------------------------

export async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "content-type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((init?.headers as Record<string, string>) ?? {}),
  };
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });
  if (!res.ok) throw new Error(`Request failed (${res.status}): ${path}`);
  return (await res.json()) as T;
}

