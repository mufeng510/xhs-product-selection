import "./globals.css";
import Link from "next/link";

export const metadata = { title: "小红书选品情报系统" };

const links = [
  ["/", "Dashboard"],
  ["/keywords", "关键词"],
  ["/products", "商品库"],
  ["/notes", "笔记"],
  ["/radar", "爆款雷达"],
  ["/accounts", "账号监控"],
  ["/tasks", "任务中心"],
  ["/system/audit", "系统审计"],
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <div className="shell">
          <nav>
            <h1>选品情报</h1>
            {links.map(([href, label]) => (
              <Link key={href} href={href}>{label}</Link>
            ))}
          </nav>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
