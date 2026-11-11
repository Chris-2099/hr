const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  return localStorage.getItem("hr_dashboard_token");
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem("hr_dashboard_token", token);
  else localStorage.removeItem("hr_dashboard_token");
}

// DEV ONLY: when the backend has DISABLE_AUTH on, this impersonates a
// seeded user without logging in (see app/deps.py X-Dev-User-Email).
function getDevUserEmail(): string | null {
  return localStorage.getItem("hr_dashboard_dev_user");
}

export function setDevUserEmail(email: string | null) {
  if (email) localStorage.setItem("hr_dashboard_dev_user", email);
  else localStorage.removeItem("hr_dashboard_dev_user");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const devUserEmail = getDevUserEmail();
  const headers: Record<string, string> = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(devUserEmail ? { "X-Dev-User-Email": devUserEmail } : {}),
  };
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
};

export interface MeResponse {
  id: number;
  email: string;
  full_name: string;
  role: string;
  can_view_compensation: boolean;
  department_scope: string[] | null;
}

export interface DevInfoResponse {
  disable_auth: boolean;
  users: { email: string; full_name: string; role: string }[];
}
