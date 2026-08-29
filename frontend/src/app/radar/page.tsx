"use client";

import { metric, useApi } from "@/lib/api";

export default function RadarPage() {
  const items = useApi<any[]>("/api/agent/notes/hot", []);
  return (
    <div className="card">
      <h2>爆款雷达</h2>
      <table>
        <thead><tr><th>笔记</th><th>热度</th><th>点赞</th><th>收藏</th><th>评论</th></tr></thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}><td>{item.title || item.source_note_id}</td><td>{metric(item.hot_score)} {item.hot_grade || ""}</td><td>{metric(item.like_count)}</td><td>{metric(item.collect_count)}</td><td>{metric(item.comment_count)}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
