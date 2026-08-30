"use client";

import { useApi } from "@/lib/api";

export default function TasksPage() {
  const data = useApi<any>("/api/tasks", { items: [] });
  const loaded = data.items !== undefined;
  return (
    <div className="card">
      <h2>任务中心</h2>
      <table>
        <thead><tr><th>类型</th><th>状态</th><th>获取</th><th>新增</th><th>错误</th></tr></thead>
        <tbody>
          {(data.items || []).map((item: any) => (
            <tr key={item.id}><td>{item.job_type}</td><td>{item.status}</td><td>{item.fetched}</td><td>{item.created_count}</td><td>{item.error || "—"}</td></tr>
          ))}
          {loaded && (data.items || []).length === 0 ? (
            <tr><td colSpan={5} className="muted">还没有任务记录。到「关键词」页点「执行」或等待定时任务运行后，这里会显示执行历史。</td></tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
