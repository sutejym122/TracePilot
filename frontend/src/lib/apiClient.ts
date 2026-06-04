// Generic typed fetch wrapper. Reused by every api/* module in later phases.
// - prepends VITE_API_BASE_URL
// - attaches Authorization: Bearer <token> when a token is present
// - normalizes the backend error envelope {"error": {"code","message"}}
// - on 401, clears the token and broadcasts an event so AuthContext can reset
import { clearToken, getToken } from "./auth";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// Event name AuthContext subscribes to for global 401 handling.
export const UNAUTHORIZED_EVENT = "tracepilot:unauthorized";

export class ApiError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

type Method = "GET" | "POST" | "PATCH" | "DELETE";

async function request<T>(
  method: Method,
  path: string,
  body?: unknown,
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    // Network failure (backend down, CORS, DNS, etc.)
    throw new ApiError(
      0,
      "network_error",
      "Unable to reach the server. Is the backend running?",
    );
  }

  if (res.status === 401) {
    // Token is invalid/expired. Clear it and let the app react globally.
    clearToken();
    window.dispatchEvent(new CustomEvent(UNAUTHORIZED_EVENT));
    throw new ApiError(
      401,
      "unauthorized",
      "Your session has expired. Please sign in again.",
    );
  }

  if (res.status === 204) {
    return undefined as T;
  }

  let data: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }

  if (!res.ok) {
    // Backend envelope: { "error": { "code", "message" } }. Fall back gracefully.
    const env = (data as { error?: { code?: string; message?: string } })
      ?.error;
    const message = env?.message ?? `Request failed with status ${res.status}`;
    const code = env?.code ?? "error";
    throw new ApiError(res.status, code, message);
  }

  return data as T;
}

export const apiGet = <T>(path: string) => request<T>("GET", path);
export const apiPost = <T>(path: string, body?: unknown) =>
  request<T>("POST", path, body);
export const apiPatch = <T>(path: string, body?: unknown) =>
  request<T>("PATCH", path, body);
export const apiDelete = <T>(path: string) => request<T>("DELETE", path);
