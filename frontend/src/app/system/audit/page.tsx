"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";

type CookieStatus = {
  kind: string;
  configured: boolean;
  source: string;
  masked: string | null;
  checked_at: string | null;
  check_status: string | null;
  check_message: string | null;
};

type Audit = { cli: string; allowlist: string[] };

const CHECK_LABEL: Record<string, string> = {
  ok: "✅ 有效",
  invalid: "⚠️ Cookie 已失效",
  error: "❌ 调用失败",
};

const KIND_LABEL: Record<string, string> = { pc: "PC Cookie", qianfan: "千帆 Cookie" };

export default function AuditPage() {
  const [audit, setAudit] = useState<Audit | null>(null);
  const [cookies, setCookies] = useState<Record<string, CookieStatus>>({});
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [auditData, cookieData] = await Promise.all([
        api<Audit>("/api/system/audit"),
        api<{ cookies: Record<string, CookieStatus> }>("/api/settings/cookies"),
      ]);
      setAudit(auditData);
      setCookies(cookieData.cookies);
    } catch {}
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const validate = useCallback(async () => {
    setBusy(true);
    setMessage("正在通过真实接口检测两个 Cookie…（约需数秒到 1 分钟）");
    try {
      const data = await api<{ cookies: Record<string, CookieStatus> }>("/api/settings/cookies/validate", { method: "POST" });
      setCookies(data.cookies);
      const parts = Object.entries(data.cookies).map(([kind, info]) => `${KIND_LABEL[kind]} ${CHECK_LABEL[info.check_status || ""] || info.check_status}`);
      setMessage(`检测完成：${parts.join("，")}${Object.values(data.cookies).some((info) => info.check_message) ? "（详情见下方）" : ""}`);
    } catch (error) {
      setMessage(`检测失败：${error}`);
    } finally {
      setBusy(false);
    }
  }, []);

  return (
    <div>
      <div className="card">
        <h2>连接检测</h2>
        <p>
          CLI 状态：<strong>{audit?.cli || "…"}</strong>（ok=采集引擎就绪）
        </p>
        <p>
          <button onClick={validate} disabled={busy}>
            {busy ? "检测中…" : "运行连接检测"}
          </button>
        </p>
        {message ? <p className="muted">{message}</p> : null}
      </div>
      <div className="card">
        <h3>Cookie 状态</h3>
        <table>
          <thead>
            <tr>
              <th>Cookie</th>
              <th>配置</th>
              <th>最近检测</th>
              <th>结果</th>
            </tr>
          </thead>
          <tbody>
            {Object.values(cookies).map((info) => (
              <tr key={info.kind}>
                <td>{KIND_LABEL[info.kind] || info.kind}</td>
                <td>{info.configured ? info.masked : "未配置"}</td>
                <td>{info.checked_at ? new Date(info.checked_at).toLocaleString("zh-CN", { hour12: false }) : "—"}</td>
                <td>
                  {info.check_status ? CHECK_LABEL[info.check_status] || info.check_status : "未检测"}
                  {info.check_message ? <div className="muted">{info.check_message}</div> : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="muted">Cookie 未配置或失效时，到「Cookie 设置」页粘贴新值保存后重试。</p>
      </div>
      <div className="card">
        <h3>允许调用的接口</h3>
        <p className="muted">{audit?.allowlist?.join("、") || "…"}</p>
        <p className="muted">禁止调用：qianfan.choose-categories（交互式命令）</p>
      </div>
    </div>
  );
}
