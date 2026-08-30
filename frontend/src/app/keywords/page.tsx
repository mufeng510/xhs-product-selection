"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";

type Keyword = {
  id: number;
  keyword: string;
  enabled: boolean;
  fetch_count: number;
  times_per_day: number;
};

type KeywordTask = {
  id: number;
  fetched: number | null;
  new_notes: number | null;
  status: string;
  error: string | null;
};

export default function KeywordsPage() {
  const [items, setItems] = useState<Keyword[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [fetchCount, setFetchCount] = useState("20");
  const [busyId, setBusyId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await api<{ items: Keyword[] }>("/api/keywords");
      setItems(data.items || []);
    } catch {}
    setLoaded(true);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const add = useCallback(async () => {
    const name = keyword.trim();
    if (!name) return;
    setMessage(null);
    try {
      await api("/api/keywords", {
        method: "POST",
        body: JSON.stringify({ keyword: name, fetch_count: Number(fetchCount) || 20, enabled: true }),
      });
      setKeyword("");
      setMessage(`已添加「${name}」，点「执行」开始采集。`);
      await load();
    } catch (error) {
      setMessage(`添加失败：${error}`);
    }
  }, [keyword, fetchCount, load]);

  const runOne = useCallback(
    async (row: Keyword) => {
      setBusyId(row.id);
      setMessage(`正在采集「${row.keyword}」…（通过真实接口抓取，约需数秒到 1 分钟）`);
      try {
        const task = await api<KeywordTask>(`/api/keywords/${row.id}/run`, { method: "POST" });
        setMessage(
          task.status === "success"
            ? `「${row.keyword}」完成：抓取 ${task.fetched} 条，新增笔记 ${task.new_notes} 条。`
            : `「${row.keyword}」失败：${task.error || task.status}`,
        );
        await load();
      } catch (error) {
        setMessage(`「${row.keyword}」执行失败：${error}`);
      } finally {
        setBusyId(null);
      }
    },
    [load],
  );

  const runAll = useCallback(async () => {
    for (const row of items.filter((item) => item.enabled)) {
      await runOne(row);
    }
  }, [items, runOne]);

  const toggle = useCallback(
    async (row: Keyword) => {
      try {
        await api(`/api/keywords/${row.id}`, {
          method: "PATCH",
          body: JSON.stringify({ keyword: row.keyword, enabled: !row.enabled, fetch_count: row.fetch_count, times_per_day: row.times_per_day }),
        });
        await load();
      } catch (error) {
        setMessage(`操作失败：${error}`);
      }
    },
    [load],
  );

  const remove = useCallback(
    async (row: Keyword) => {
      if (!window.confirm(`删除关键词「${row.keyword}」？`)) return;
      try {
        await api(`/api/keywords/${row.id}`, { method: "DELETE" });
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
        <h2>关键词</h2>
        <p className="muted">添加关键词后点「执行」开始采集笔记；定时任务也会自动执行启用的关键词。</p>
        <p>
          <input
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            placeholder="输入关键词，如：防晒霜"
            onKeyDown={(event) => {
              if (event.key === "Enter") add();
            }}
            style={{ width: "240px" }}
          />{" "}
          每次条数{" "}
          <input
            value={fetchCount}
            onChange={(event) => setFetchCount(event.target.value)}
            type="number"
            min={1}
            max={100}
            style={{ width: "80px" }}
          />{" "}
          <button onClick={add} disabled={!keyword.trim()}>
            添加
          </button>{" "}
          <button onClick={runAll} disabled={busyId !== null || !items.some((item) => item.enabled)}>
            {busyId !== null ? "执行中…" : "执行全部启用"}
          </button>
        </p>
        {message ? <p className="muted">{message}</p> : null}
      </div>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>关键词</th>
              <th>状态</th>
              <th>每次条数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.id}>
                <td>{row.keyword}</td>
                <td>{row.enabled ? "启用" : "停用"}</td>
                <td>{row.fetch_count}</td>
                <td>
                  <button onClick={() => runOne(row)} disabled={busyId !== null}>
                    {busyId === row.id ? "执行中…" : "执行"}
                  </button>{" "}
                  <button onClick={() => toggle(row)} disabled={busyId !== null}>
                    {row.enabled ? "停用" : "启用"}
                  </button>{" "}
                  <button onClick={() => remove(row)} disabled={busyId !== null}>
                    删除
                  </button>
                </td>
              </tr>
            ))}
            {loaded && items.length === 0 ? (
              <tr>
                <td colSpan={4} className="muted">
                  还没有关键词。先到「Cookie 设置」配置并通过检测，再在上方添加第一个关键词开始采集。
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
