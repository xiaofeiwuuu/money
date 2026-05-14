# 家庭账本

支付宝/微信账单导入与分析工具。当前为 V0 阶段（单用户、无认证）。

## 技术栈

- **框架**：Next.js 16 (App Router) + TypeScript
- **样式**：Tailwind CSS v4 + shadcn/ui
- **数据库**：Supabase PostgreSQL
- **ORM**：Prisma 7（pg adapter）
- **解析**：papaparse + xlsx + iconv-lite（GBK 兼容）
- **图表**：Recharts
- **包管理**：pnpm

## 当前功能（V0）

- ✅ 上传支付宝/微信账单（CSV / XLSX）
- ✅ 自动识别来源 + 跳过头部说明行
- ✅ 北京时区时间解析
- ✅ 预览（前 100 条 + 失败行明细）
- ✅ 写入数据库（基于 `source + orderId` 去重）
- ✅ 交易列表（日期/方向/来源/关键字筛选）
- ✅ 月度收支柱状图（最近 12 个月）

## 路线图

- **V1**：Supabase Auth + 家庭共享（所有成员同等权限）
- **V2**：分类管理 + 分类占比环形图 + 年度趋势 + 同环比
- **V3+**：预算、手动记账、AI 自动分类、OCR

详见 [REQUIREMENTS.md](./REQUIREMENTS.md)。

## 本地开发

```bash
pnpm install
pnpm dev
```

打开 http://localhost:3000

### 环境变量

新建 `.env` 文件，填入 Supabase 连接字符串：

```env
DATABASE_URL="postgresql://<user>:<password>@<pooler-host>:5432/postgres"
```

### 数据库

```bash
pnpm dlx prisma migrate dev    # 应用迁移
pnpm dlx prisma generate       # 生成客户端
pnpm dlx prisma studio         # 浏览数据
```

## 项目结构

```
src/
├── app/
│   ├── api/
│   │   ├── import/parse        解析上传的账单
│   │   ├── import/commit       去重写入数据库
│   │   ├── transactions        列表 / 删除
│   │   └── analytics/monthly   月度聚合
│   ├── import/                 导入页（上传→预览→提交）
│   ├── transactions/           交易列表页
│   └── analytics/              分析页（柱状图）
├── components/
│   ├── ui/                     shadcn 组件
│   └── nav.tsx                 顶部导航
├── lib/
│   ├── db.ts                   Prisma 客户端单例
│   ├── types.ts                共享类型
│   └── parsers/                支付宝/微信解析器
└── generated/prisma/           Prisma 生成的客户端（gitignored）
```

## 安全提醒

- `samples/`（真实账单）已 gitignore，请勿提交
- `.env`（数据库密码）已 gitignore
- 部署时务必使用 Supabase RLS 或应用层鉴权（V1 起）
