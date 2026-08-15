const BASE = process.env.NEXT_PUBLIC_API_BASE || process.env.API_INTERNAL_BASE || "http://localhost:8000";

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store", ...init, headers: { "Content-Type": "application/json", ...(init?.headers || {}) } });
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  return res.json() as Promise<T>;
}

export function metric(value: number | null | undefined): string {
  return value === null || value === undefined ? "—" : String(value);
}
