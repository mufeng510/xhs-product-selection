"use client";

import { useCallback, useEffect, useState } from "react";
import { api, metric } from "@/lib/api";

type Account = {
  id: number;
  source: string;
  source_user_id: string;
  nickname: string | null;
  followers: number | null;
  monitor_enabled: boolean;
};

export default function AccountsPage() {
  const [items, setItems] = useState<Account[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [userId, setUserId] = useState("");
  const [profileUrl, setProfileUrl] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await api<{ items: Account[] }>("/api/accounts");
      setItems(data.items || []);
    } catch {}
    setLoaded(true);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const add = useCallback(async () => {
    const id = userId.trim();
    if (!id) return;
    setMessage(null);
    try {
      await api("/api/accounts", {
        method: "POST",
        body: JSON.stringify({ source: "pc", source_user_id: id, profile_url: profileUrl.trim() || null }),
      });
      setUserId("");
      setProfileUrl("");
      setMessage("已添加监控账号，点「执行」拉取该用户最新笔记。");
      await load();
    } catch (error) {
      setMessage(`添加失败：${error}`);
    }
  }, [userId, profileUrl, load]);

  const runOne = useCallback(
    async (row: Account) => {
      setBusyId(row.id);
      setMessage(`正在拉取用户 ${row.source_user_id} 的笔记…`);
      try {
        await api(`/api/accounts/${row.id}/run`, { method: "POST" });
        setMessage(`用户 ${row.nickname || row.source_user_id} 执行完成。`);
        await load();
      } catch (error) {
        setMessage(`执行失败：${error}`);
      } finally {
        setBusyId(null);
      }
    },
    [load],
  );

  const toggle = useCallback(
    async (row: Account) => {
      try {
        await api(`/api/accounts/${row.id}`, { method: "PATCH", body: JSON.stringify({ monitor_enabled: !row.monitor_enabled }) });
        await load();
      } catch (error) {
        setMessage(`操作失败：${error}`);
      }
    },
    [load],
  );

  const remove = useCallback(
    async (row: Account) => {
      if (!window.confirm(`删除监控账号 ${row.nickname || row.source_user_id}？`)) return;
      try {
        await api(`/api/accounts/${row.id}`, { method: "DELETE" });
        await load();
      } catch (error) {
        setMessage(`删除失败：${error}`);
      }
    },
    [load],
  );

  return (
    <div>
      <div className="card">
        <h2>账号监控</h2>
        <p className="muted">添加小红书用户 ID（主页链接 /user/profile/ 后面那段），定时任务会自动检查新笔记。</p>
        <p>
          <input
            value={userId}
            onChange={(event) => setUserId(event.target.value)}
            placeholder="用户 ID，如 5ff0e6410000000001008400"
            style={{ width: "280px" }}
          />{" "}
          <input
            value={profileUrl}
            onChange={(event) => setProfileUrl(event.target.value)}
            placeholder="主页链接（可选）"
            style={{ width: "300px" }}
          />{" "}
          <button onClick={add} disabled={!userId.trim()}>
            添加
          </button>
        </p>
        {message ? <p className="muted">{message}</p> : null}
      </div>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>来源</th>
              <th>用户ID</th>
              <th>昵称</th>
              <th>粉丝</th>
              <th>监控</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.id}>
                <td>{row.source}</td>
                <td>{row.source_user_id}</td>
                <td>{row.nickname || "—"}</td>
                <td>{metric(row.followers)}</td>
                <td>{row.monitor_enabled ? "开" : "关"}</td>
                <td>
                  <button onClick={() => runOne(row)} disabled={busyId !== null}>
                    {busyId === row.id ? "执行中…" : "执行"}
                  </button>{" "}
                  <button onClick={() => toggle(row)} disabled={busyId !== null}>
                    {row.monitor_enabled ? "关闭监控" : "开启监控"}
                  </button>{" "}
                  <button onClick={() => remove(row)} disabled={busyId !== null}>
                    删除
                  </button>
                </td>
              </tr>
            ))}
            {loaded && items.length === 0 ? (
              <tr>
                <td colSpan={6} className="muted">
                  还没有监控账号。粘贴用户 ID 或主页链接添加，用于追踪竞品/达人笔记。
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
