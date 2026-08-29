# 小红书选品情报系统

个人 NAS / 家用服务器上的小红书选品情报系统。通过独立 Adapter 调用开源 All-IN-ONE（`aione` CLI），不修改 All-IN-ONE 本体。

## 功能

- 关键词采集笔记、去重、商品候选提取
- 账号监控与新笔记识别
- 商品/店铺库、每日快照、趋势（无历史则返回 null）
- 爆款评分（可配置权重，0–100）
- QianFan `user-shop` 店铺匹配（不是通用商品目录）
- 企业微信 Webhook 通知
- Web 管理后台与 XHS 接口审计
- AI / Agent API 预留（第一版为 Mock）

## 架构

```
单个容器（app :8000）
    FastAPI（API + 托管 Next.js 静态页面）
        → SQLite（/data/app/xhs_selection.db，默认）
        → All-IN-ONE + Spider_XHS（采集引擎）
```

All-IN-ONE 只作为采集引擎，安装在镜像内。前后端打包为**一个镜像、一个进程、一个端口**，数据库默认使用 SQLite 文件，无需额外服务。

## 目录结构

- `backend/` FastAPI、Alembic、Adapter、任务
- `frontend/` Next.js（构建时静态导出，由 FastAPI 托管）
- `scripts/` 初始化、健康检查、备份、接口审计
- `tests/` 单元测试
- `Dockerfile/` 根目录单镜像构建（Node 构建前端 → Python 运行时）

## Docker 部署

```bash
cp .env.example .env
docker compose up -d
```

或者不用 compose，一条命令直接跑：

```bash
docker run -d --name xhs-selection -p 8000:8000 -v xhs-data:/data jerry0510/xhs-product-selection:latest
```

打开 `http://服务器IP:8000`，看到「欢迎使用小红书选品情报系统」。

启动时自动：Alembic migrate（建表到 SQLite）→ 启动 API → 同端口托管前端页面。

## 环境变量

见 `.env.example`。关键项：

- `DATABASE_URL` 默认 SQLite，如需 PostgreSQL 改成 `postgresql+asyncpg://用户:密码@主机:5432/库名` 即可
- `APP_PORT` 宿主机端口（默认 8000）
- `AIONE_XHS_PC_COOKIES` PC 笔记/用户接口
- `AIONE_XHS_QIANFAN_COOKIES` 千帆接口
- `XHS_COOKIE` 仅作为 PC cookie 别名
- `WECHAT_WEBHOOK_URL` 企业微信机器人

不要把 Cookie 提交到 Git。

## 小红书登录配置

推荐把 cookie 写入环境变量，或挂载到容器 `/data/xhs`（`XDG_CONFIG_HOME`）。

All-IN-ONE 实际 cookie 文件位置：

`$XDG_CONFIG_HOME/aione/xhs/{profile}.json`

PC 使用 profile `pc`，千帆使用 `qianfan`。`AIONE_XHS_COOKIES` 只对 profile `default` 生效，不能直接给 `note search` 用。

## QianFan 配置

必须使用千帆 cookie。第一版匹配路径：

```
笔记候选 → 可选 qianfan user-by-page --choice -1 → user-shop(buyer_id) → shops
```

`user-shop` 是分销商合作店铺，不是商品目录。销量/评价/价格若接口未提供则为 NULL。

禁止调用交互式 `choose-categories`。

## 与 All-IN-ONE 实际差异

1. 真实 HTTP 在 `aione setup` 克隆的 Spider_XHS，不在 All-IN-ONE 仓库本体。
2. 镜像需要 Python + Node + Git。
3. `user-by-page` 需要 `choice` + `distribution-category`；MVP 使用 `--choice -1`。
4. Cookie 环境变量以 `AIONE_XHS_PC_COOKIES` / `AIONE_XHS_QIANFAN_COOKIES` 为准。
5. 当前 Spider_XHS 的 `XHS_Apis` 需要 `XHSPcAuth`。Adapter 先走 CLI；若构造失败，仅在 Adapter 内使用 `XHSPcAuth.from_cookie` 兜底。
6. 不要把 `XDG_DATA_HOME` 指到空的 cookie 卷，以免盖住镜像内烘焙的 `/app/upstreams`。

## 数据库

默认 SQLite（WAL 模式，文件在数据卷 `/data/app/xhs_selection.db`），单机个人部署足够。需要 PostgreSQL 时只改 `DATABASE_URL`，Schema 完全一致，变更只走 Alembic。

## 定时任务

APScheduler 跑在唯一 backend 进程内：关键词约 12 小时，账号约 6 小时。也可在 Web 点「立即执行」。

## 微信通知

`NotificationProvider` + 企业微信 Webhook。默认只推重要事件（新爆款等）。

## 接口文档

后端启动后访问 `http://服务器IP:8000/docs`。

## 故障排查

- `/health` 中 `xhs_adapter=ok` 只表示 CLI 和 upstream 存在，不表示已登录。
- 审计页商品字段全 ❌：尚未用真实 cookie 拉过千帆 JSON，属预期。
- 采集失败：检查 PC / 千帆 cookie 是否分别配置。
- SQLite 报 `database is locked`：已默认开启 WAL + busy_timeout，一般不会出现；若仍遇到，说明有长事务，重启容器即可。

## 备份恢复

```bash
./scripts/backup.sh
```

SQLite 数据库文件备份保存在 `./backup/`。恢复时停容器，把备份文件放回数据卷 `/data/app/xhs_selection.db` 再启动。

## 升级

拉取新版本后 `docker compose pull && docker compose up -d`（本地构建则 `docker compose build`）。容器启动会自动 migrate。不要在容器里手动改库结构。
