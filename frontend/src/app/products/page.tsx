import Link from "next/link";
import { api, metric } from "@/lib/api";

export default async function ProductsPage() {
  let data: any = { items: [] };
  try { data = await api("/api/products"); } catch {}
  return (
    <div className="card">
      <h2>商品库</h2>
      <table>
        <thead><tr><th>名称</th><th>品牌</th><th>价格</th><th>销量</th><th>状态</th></tr></thead>
        <tbody>
          {(data.items || []).map((item: any) => (
            <tr key={item.id}>
              <td><Link href={`/products/${item.id}`}>{item.product_name || "未命名"}</Link></td>
              <td>{item.brand || "—"}</td>
              <td>{metric(item.current_price)}</td>
              <td>{metric(item.current_sales)}</td>
              <td>{item.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
