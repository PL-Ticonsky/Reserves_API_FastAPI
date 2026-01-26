import { clearToken, getToken } from "@/lib/auth";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL!;

type ApiError = {
  status: number;
  code?: string;
  message: string;
  raw?: any;
};

async function parseJsonSafe(res: Response) {
  const text = await res.text();
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return text || null;
  }
}

export async function api<T>(
  path: string,
  opts: RequestInit & { auth?: boolean } = {}
): Promise<T> {
  const headers = new Headers(opts.headers || {});
  headers.set("Content-Type", "application/json");

  if (opts.auth !== false) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...opts,
    headers,
    cache: "no-store",
  });

  const data = await parseJsonSafe(res);

  if (res.status === 401) {
    // token expiro o invalido → logout duro
    clearToken();
    // redirigir desde client runtime
    if (typeof window !== "undefined") window.location.href = "/login";
  }

  if (!res.ok) {
    const code =
      (data && (data.detail?.code || data.code || data.detail)) || undefined;

    const msg =
      (data && (data.detail?.message || data.message || data.detail)) ||
      `Request failed (${res.status})`;

    const err: ApiError = { status: res.status, code, message: msg, raw: data };
    throw err;
  }

  return data as T;
}
