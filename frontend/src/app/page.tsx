"use client";

import { api, metric, useApi } from "@/lib/api";

export default function Page() {
  const data = useApi<any>("/api/dashboard", {});
  return (
    <div>
      <div className="card">
        <h2>欢迎使用小红书选品情报系统</h2>
        <p className="muted">开始采集三步走：① 「Cookie 设置」粘贴 Cookie 并检测通过 → ② 「关键词」添加关键词 → ③ 点「执行」采集。数据会出现在商品库、笔记和爆款雷达。</p>
      </div>
      <div className="grid">
        <div className="card"><div className="muted">今日新增商品</div><strong>{metric(data.today_new_products)}</strong></div>
        <div className="card"><div className="muted">今日新增笔记</div><strong>{metric(data.today_new_notes)}</strong></div>
        <div className="card"><div className="muted">7日新品</div><strong>{metric(data.week_new_products)}</strong></div>
        <div className="card"><div className="muted">监控账号</div><strong>{metric(data.monitored_accounts)}</strong></div>
      </div>
    </div>
  );
}
