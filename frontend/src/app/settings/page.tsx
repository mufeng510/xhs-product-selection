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

const KIND_LABEL: Record<string, string> = {
  pc: "PC Cookie",
  qianfan: "千帆 Cookie",
};

const KIND_DESC: Record<string, string> = {
  pc: "用于笔记搜索、笔记详情、用户监控等 PC 端接口。",
  qianfan: "用于千帆 user-shop 店铺匹配接口。",
};

const SOURCE_LABEL: Record<string, string> = {
  db: "页面保存",
  none: "未配置",
};

const CHECK_LABEL: Record<string, string> = {
  ok: "✅ 有效",
  invalid: "⚠️ Cookie 已失效",
  error: "❌ 调用失败",
};

function sourceLabel(source: string): string {
  if (SOURCE_LABEL[source]) return SOURCE_LABEL[source];
  if (source.startsWith("env:")) return `环境变量 ${source.slice(4)}`;
  return source;
}

function formatTime(iso: string | null): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("zh-CN", { hour12: false });
  } catch {
    return iso;
  }
}

function CookieCard({ kind, info, onChanged }: { kind: string; info: CookieStatus | undefined; onChanged: () => void }) {
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState<"" | "save" | "validate">("");
  const [message, setMessage] = useState<string | null>(null);

  const validate = useCallback(async () => {
    setBusy("validate");
    setMessage(null);
    try {
      const data = await api<{ cookies: Record<string, CookieStatus> }>(
        `/api/settings/cookies/validate?kind=${kind}`,
        { method: "POST" },
      );
      const check = data.cookies[kind];
      if (check) {
        const label = CHECK_LABEL[check.check_status || ""] || check.check_status;
        setMessage(`${label}${check.check_message ? "：" + check.check_message : ""}`);
      }
      onChanged();
    } catch (error) {
      setMessage(`检测失败：${error}`);
    } finally {
      setBusy("");
    }
  }, [kind, onChanged]);

  const save = useCallback(async () => {
    setBusy("save");
    setMessage(null);
    try {
      await api("/api/settings/cookies", {
        method: "PUT",
        body: JSON.stringify(kind === "pc" ? { pc_cookie: value } : { qianfan_cookie: value }),
      });
      setValue("");
      setMessage("已保存，立即生效（下一次采集请求即使用新 Cookie）");
      onChanged();
    } catch (error) {
      setMessage(`保存失败：${error}`);
    } finally {
      setBusy("");
    }
  }, [kind, value, onChanged]);

  return (
    <div className="card">
      <h2>{KIND_LABEL[kind]}</h2>
      <p className="muted">{KIND_DESC[kind]}</p>
      <table>
        <tbody>
          <tr>
            <td>状态</td>
            <td>
              {info?.configured ? "已配置" : "未配置"}（来源：{sourceLabel(info?.source || "none")}）
            </td>
          </tr>
          <tr>
            <td>当前值</td>
            <td>{info?.configured ? info.masked : "—"}</td>
          </tr>
          <tr>
            <td>最近检测</td>
            <td>
              {info?.check_status ? CHECK_LABEL[info.check_status] || info.check_status : "未检测"}
              （{formatTime(info?.checked_at ?? null)}）
              {info?.check_message ? <div className="muted">{info.check_message}</div> : null}
            </td>
          </tr>
        </tbody>
      </table>
      <p>
        <textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="粘贴新的 Cookie 字符串（留空保存则清除页面配置，回退到环境变量）"
          style={{ width: "100%", minHeight: "72px", fontFamily: "monospace", fontSize: 12 }}
        />
      </p>
      <p>
        <button onClick={save} disabled={busy !== "" || value.trim() === ""}>
          {busy === "save" ? "保存中…" : "保存"}
        </button>{" "}
        <button onClick={validate} disabled={busy !== ""}>
          {busy === "validate" ? "检测中（约数秒）…" : "检测有效性"}
        </button>
      </p>
      {message ? <p className="muted">{message}</p> : null}
    </div>
  );
}

export default function SettingsPage() {
  const [cookies, setCookies] = useState<Record<string, CookieStatus>>({});

  const load = useCallback(async () => {
    try {
      const data = await api<{ cookies: Record<string, CookieStatus> }>("/api/settings/cookies");
      setCookies(data.cookies);
    } catch {}
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div>
      <div className="card">
        <h2>Cookie 设置</h2>
        <p className="muted">
          Cookie 过期后无需改环境变量重启容器：在下方粘贴新值保存即可，保存后立即生效，可用于检测是否有效。
          页面保存的值优先于环境变量；清除页面值后回退到环境变量。完整 Cookie 不会回显，只显示掩码。
        </p>
      </div>
      <CookieCard kind="pc" info={cookies.pc} onChanged={load} />
      <CookieCard kind="qianfan" info={cookies.qianfan} onChanged={load} />
    </div>
  );
}
