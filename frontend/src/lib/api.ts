"use client";

import { useEffect, useState } from "react";

// 单镜像部署时构建为空字符串（同源请求）；本地开发默认指向 http://localhost:8000
const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store", ...init, headers: { "Content-Type": "application/json", ...(init?.headers || {}) } });
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  return res.json() as Promise<T>;
}

export function useApi<T>(path: string, initial: T): T {
  const [data, setData] = useState<T>(initial);
  useEffect(() => {
    if (!path) return;
    let cancelled = false;
    api<T>(path)
      .then((value) => {
        if (!cancelled) setData(value);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [path]);
  return data;
}

export function metric(value: number | null | undefined): string {
  return value === null || value === undefined ? "—" : String(value);
}
