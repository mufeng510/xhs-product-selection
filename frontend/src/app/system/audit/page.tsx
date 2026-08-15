import { api } from "@/lib/api";

export default async function AuditPage() {
  let data: any = { product_fields: {} };
  try { data = await api("/api/system/audit"); } catch {}
  const fields = data.product_fields || {};
  return (
    <div className="card">
      <h2>XHS 接口审计</h2>
      <p>CLI：{data.cli || "—"}　最近执行：{data.ran_at || "—"}</p>
      <table>
        <thead><tr><th>商品字段</th><th>发现</th></tr></thead>
        <tbody>
          {Object.entries(fields).map(([k, v]) => (
            <tr key={k}><td>{k}</td><td>{v ? "✅" : "❌"}</td></tr>
          ))}
        </tbody>
      </table>
      <p className="muted">{data.note}</p>
    </div>
  );
}
