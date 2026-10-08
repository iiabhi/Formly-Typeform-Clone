import { API_URL } from "@/lib/config";

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: unknown,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = Omit<RequestInit, "body"> & { body?: unknown };

function messageFromDetail(detail: unknown, fallback: string): string {
  return typeof detail === "string" ? detail : fallback;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, headers, ...rest } = options;
  const response = await fetch(`${API_URL}/api${path}`, {
    ...rest,
    headers: { ...(body !== undefined ? { "Content-Type": "application/json" } : {}), ...headers },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const payload: { detail?: unknown } | null = await response.json().catch(() => null);
    const detail = payload?.detail;
    throw new ApiError(
      response.status,
      detail,
      messageFromDetail(detail, `Request failed (${response.status})`),
    );
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}
