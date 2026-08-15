import { api, metric } from "@/lib/api";

export default async function AccountsPage() {
  let data: any = { items: [] };
  try { data = await api("/api/accounts"); } catch {}
  return (
    <div className="card">
      <h2>账号监控</h2>
      <table>
        <thead><tr><th>来源</th><th>用户ID</th><th>昵称</th><th>粉丝</th><th>监控</th></tr></thead>
        <tbody>
          {(data.items || []).map((item: any) => (
            <tr key={item.id}><td>{item.source}</td><td>{item.source_user_id}</td><td>{item.nickname || "—"}</td><td>{metric(item.followers)}</td><td>{item.monitor_enabled ? "开" : "关"}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
