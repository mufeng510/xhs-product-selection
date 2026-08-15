import { api } from "@/lib/api";

export default async function KeywordsPage() {
  let data: any = { items: [] };
  try { data = await api("/api/keywords"); } catch {}
  return (
    <div className="card">
      <h2>关键词</h2>
      <table>
        <thead><tr><th>关键词</th><th>状态</th><th>每次条数</th></tr></thead>
        <tbody>
          {(data.items || []).map((item: any) => (
            <tr key={item.id}><td>{item.keyword}</td><td>{item.enabled ? "启用" : "停用"}</td><td>{item.fetch_count}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
