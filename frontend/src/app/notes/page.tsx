"use client";

import { metric, useApi } from "@/lib/api";

export default function NotesPage() {
  const data = useApi<any>("/api/notes", { items: [] });
  return (
    <div className="card">
      <h2>笔记</h2>
      <table>
        <thead><tr><th>标题</th><th>作者</th><th>点赞</th><th>热度</th></tr></thead>
        <tbody>
          {(data.items || []).map((item: any) => (
            <tr key={item.id}><td>{item.title || item.source_note_id}</td><td>{item.author_name || "—"}</td><td>{metric(item.like_count)}</td><td>{metric(item.hot_score)} {item.hot_grade || ""}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
