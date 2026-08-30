"use client";

import { metric, useApi } from "@/lib/api";

export default function ProductsPage() {
  const data = useApi<any>("/api/products", { items: [] });
  const loaded = data.items !== undefined;
  return (
    <div className="card">
      <h2>商品库</h2>
      <table>
        <thead><tr><th>名称</th><th>品牌</th><th>价格</th><th>销量</th><th>状态</th></tr></thead>
        <tbody>
          {(data.items || []).map((item: any) => (
            <tr key={item.id}>
              <td><a href={`/products/detail?id=${item.id}`}>{item.product_name || "未命名"}</a></td>
              <td>{item.brand || "—"}</td>
              <td>{metric(item.current_price)}</td>
              <td>{metric(item.current_sales)}</td>
              <td>{item.status}</td>
            </tr>
          ))}
          {loaded && (data.items || []).length === 0 ? (
            <tr><td colSpan={5} className="muted">还没有商品。商品从笔记内容中自动提取，先到「关键词」页执行一次采集。</td></tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
