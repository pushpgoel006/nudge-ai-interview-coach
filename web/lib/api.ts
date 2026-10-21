/** Thin client for the Nudge API. Same-origin: /api/* is proxied to the Python backend. */

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

type FieldIssue = { loc?: (string | number)[]; msg?: string };

function messageFrom(detail: unknown, fallback: string): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const first = detail[0] as FieldIssue | undefined;
    const field = first?.loc?.filter((p) => p !== "body").join(" ");
    if (first?.msg) return field ? `${field}: ${first.msg}` : first.msg;
  }
  return fallback;
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const isForm = typeof FormData !== "undefined" && body instanceof FormData;
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      method,
      credentials: "same-origin",
      headers: body !== undefined && !isForm ? { "Content-Type": "application/json" } : undefined,
      body: body === undefined ? undefined : isForm ? (body as FormData) : JSON.stringify(body),
    });
  } catch {
    throw new ApiError("Can't reach the server. Check your connection and try again.", 0);
  }

  if (response.status === 204) return undefined as T;

  let data: unknown = null;
  try {
    data = await response.json();
  } catch {
    /* non-JSON error body */
  }
  if (!response.ok) {
    const detail = (data as { detail?: unknown } | null)?.detail;
    throw new ApiError(messageFrom(detail, `Something went wrong (${response.status}).`), response.status);
  }
  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body ?? {}),
  upload: <T>(path: string, form: FormData) => request<T>("POST", path, form),
  del: <T = void>(path: string) => request<T>("DELETE", path),
};

/* ---------- shared types ---------- */

export type User = { id: string; email: string; display_name: string };

export type PrepSession = {
  id: string;
  company_name: string;
  role: string;
  jd_text: string;
  status: string;
  created_at: string | null;
};

export type Source = { file_name: string; page: number; doc_type: string | null };
