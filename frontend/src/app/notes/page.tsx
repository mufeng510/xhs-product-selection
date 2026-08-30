"use client";

import { metric, useApi } from "@/lib/api";

export default function NotesPage() {
  const data = useApi<any>("/api/notes", { items: [] });
  const loaded = data.items !== undefined;
  return (
    <div className="card">
      <h2>笔记</h2>
      <table>
        <thead><tr><th>标题</th><th>作者</th><th>点赞</th><th>热度</th></tr></thead>
        <tbody>
          {(data.items || []).map((item: any) => (
            <tr key={item.id}><td>{item.title || item.source_note_id}</td><td>{item.author_name || "—"}</td><td>{metric(item.like_count)}</td><td>{metric(item.hot_score)} {item.hot_grade || ""}</td></tr>
          ))}
          {loaded && (data.items || []).length === 0 ? (
            <tr><td colSpan={4} className="muted">还没有笔记。到「关键词」页添加关键词并执行采集后，这里会展示抓取到的笔记。</td></tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
