# 家庭记账系统 - 需求文档

> 版本：v0.2（精简版）· 日期：2026-05-13

---

## 一、目标与边界

### 做什么
为家庭提供共享的账单导入和分析工具，主要解决：
- 支付宝/微信账单批量导入（不手动录入）
- 数据分析（年度对比、分类占比、趋势）

### 不做什么
- ❌ 手机 App（PWA 自适应即可）
- ❌ 股票/投资追踪
- ❌ 企业财务

---

## 二、技术栈

| 层级 | 选型 |
|---|---|
| 框架 | Next.js 15 (App Router) |
| 样式 | Tailwind + shadcn/ui |
| 数据库 | Supabase PostgreSQL |
| ORM | Prisma |
| 认证 | Supabase Auth（V1 加） |
| 图表 | Recharts |
| 解析 | papaparse + xlsx |
| 包管理 | pnpm |
| 部署 | Vercel |

---

## 三、版本规划（分三步走，每步都可用）

### 🎯 V0（当前目标 - 3 天 - 自己一个人用）

| 编号 | 功能 |
|---|---|
| F1 | **上传** — 拖拽/点击上传 CSV/XLSX |
| F2 | **预览** — 解析后展示前 100 行 + 元信息（格式、跳过行、异常行） |
| F3 | **字段映射** — 自动映射 + 手动调整（日期/金额/方向/订单号） |
| F4 | **导入** — 去重写入数据库（提示新增 N 条、已存在 M 条） |
| F5 | **交易列表** — 分页 + 筛选（日期/收支/关键字） |
| F6 | **月度图表** — 收支柱状图（最近 12 个月） |

**V0 不做**：认证、家庭、多用户、权限、角色、邀请、分类管理、预算、AI

---

### V1（再 3 天 - 家人能用）

- F7 邮箱密码登录（Supabase Auth）
- F8 一个家庭模型（用户首次登录自动建）
- F9 所有家庭成员同等权限（先不分角色）
- F10 家人账号 = 你在 Supabase 后台手动建（不做邀请系统）

---

### V2（再 3 天 - 分析丰富）

- F11 分类管理（自定义 + 默认）
- F12 分类占比环形图
- F13 年度趋势折线图
- F14 同比/环比
- F15 日历热力图

---

### V3+（长期，不规划细节）

预算、手动记账、模板、附件、AI 分类、OCR、银行卡账单、第三方登录…

---

## 四、V0 详细需求

### F1 上传
- 拖拽或点击选择
- 支持 `.csv`、`.xlsx`、`.xls`
- 自动识别支付宝/微信
- 单文件 ≤ 10MB
- 客户端解析（账单不上传服务器原文件，只上传解析后数据）

### F2 预览
- 表格展示前 100 行（虚拟滚动）
- 元信息：识别格式、跳过行数、总行数、异常行数
- 异常行高亮（金额无法解析、日期错误）

### F3 字段映射
- 自动映射（基于来源预设规则）
- 必填：日期、金额、方向、订单号
- 可选：商家、备注
- 列下拉选择对应字段

### F4 导入
- 基于 `source + order_id` 去重
- 展示「新增 N 条 / 已存在 M 条 / 失败 K 条」
- 失败行可下载错误报告

### F5 交易列表
- 分页（每页 50）或虚拟滚动
- 筛选：日期范围、收/支、关键字搜索
- 编辑：备注（其他字段先不开放编辑）
- 删除单条 / 批量删除

### F6 月度图表
- 最近 12 个月收支柱状图
- 收入绿、支出红
- 鼠标悬停显示当月明细数字

---

## 五、V0 数据模型

```prisma
model Transaction {
  id              String   @id @default(cuid())
  source          String   // "alipay" | "wechat"
  orderId         String   // 来源订单号
  transactionDate DateTime
  amount          Decimal  @db.Decimal(12, 2)
  direction       String   // "income" | "expense"
  merchant        String?
  description     String?
  rawData         Json?    // 原始行数据（备查）
  createdAt       DateTime @default(now())

  @@unique([source, orderId])
  @@index([transactionDate])
}

model ImportSession {
  id           String   @id @default(cuid())
  source       String
  filename     String
  totalRows    Int
  insertedRows Int
  skippedRows  Int
  failedRows   Int
  createdAt    DateTime @default(now())
}
```

---

## 六、V0 页面路由

```
/                    首页 → 重定向 /transactions
/import              上传页（包含整个 上传→预览→映射→导入 流程）
/transactions        交易列表
/analytics           月度图表

/api/import/parse    解析文件（服务端，处理 GBK 编码）
/api/import/commit   写入数据库
/api/transactions    列表 / CRUD
/api/analytics/monthly  月度聚合
```

---

## 七、V0 不解决的问题（明确延后）

- 多用户认证 → V1
- 家庭共享 → V1
- 权限管理 → V1
- 分类系统 → V2
- 预算/提醒 → V3+
- AI/OCR → V3+

---

## 八、下一步

1. 初始化 Next.js 项目
2. 装依赖
3. 配 Supabase + Prisma
4. 建表
5. 实现 F1-F6

> 文档约定：完成的功能在编号前打 ✅
