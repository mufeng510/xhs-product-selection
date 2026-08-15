import { api, metric } from "@/lib/api";

export default async function ProductDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let item: any = {};
  try { item = await api(`/api/products/${id}`); } catch {}
  return (
    <div className="card">
      <h2>{item.product_name || "商品详情"}</h2>
      <p>店铺：{item.shop_name || "—"}</p>
      <p>价格：{metric(item.current_price)}</p>
      <p>销量：{metric(item.current_sales)}</p>
      <p>评价：{metric(item.current_review_count)}</p>
      <p>24h销量变化：{metric(item.sales_growth_1d)}</p>
      <p>数据来源：{item.source || "—"}</p>
      <p className="muted">趋势图将在有快照后展示。缺失字段显示为 —，不会伪造 0。</p>
    </div>
  );
}
