# 收入支出管理系统 - 需求文档

## 项目概述

一个支持支付宝、微信等平台 CSV 导入的个人/家庭收支管理工具，提供数据可视化、智能分类、预算管理等功能。

---

## 功能模块

### 1. 数据导入

#### 1.1 CSV 解析
- [ ] 支付宝账单 CSV 解析
- [ ] 微信账单 CSV 解析
- [ ] 银行卡账单 CSV 解析（招行、工行等）
- [ ] 格式版本适配机制（平台 CSV 格式可能变化）

#### 1.2 数据去重
- [ ] 组合字段去重（时间 + 金额 + 商户 + 备注）
- [ ] 交易号去重（如有）
- [ ] 重复数据预览确认

#### 1.3 手动记账
- [ ] 自定义收入/支出录入
- [ ] 快捷模板（常用支出一键记录）
- [ ] 拍照记账（OCR 识别小票）

---

### 2. 用户体系

#### 2.1 账户管理
- [ ] 注册 / 登录
- [ ] 第三方登录（微信、Apple）
- [ ] 密码找回

#### 2.2 多设备同步
- [ ] 云端数据同步
- [ ] 离线优先（本地先存，联网同步）
- [ ] 冲突解决策略

---

### 3. 账户与家庭

#### 3.1 个人账户
- [ ] 多平台账单汇总（支付宝 + 微信 + 银行卡）
- [ ] 账户余额管理

#### 3.2 家庭账户
- [ ] 家庭创建与成员邀请
- [ ] 成员角色（管理员 / 成员）
- [ ] 家庭总收支统计
- [ ] 家庭储蓄目标

#### 3.3 隐私控制
- [ ] 隐私交易（仅自己可见）
- [ ] 家庭成员可见范围设置（明细 / 仅汇总）

---

### 4. 数据分析

#### 4.1 图表展示
- [ ] 收支饼图（分类占比）
- [ ] 趋势折线图（月度/年度趋势）
- [ ] 日历热力图（每日花销）
- [ ] 柱状图对比（月度对比）

#### 4.2 分类统计
- [ ] 预设分类：餐饮、交通、购物、娱乐、居住、医疗、教育、投资、转账等
- [ ] 自定义分类
- [ ] 分类下钻（餐饮 → 外卖 / 堂食 / 买菜）

#### 4.3 周期分析
- [ ] 月度报表
- [ ] 年度报表
- [ ] 同比分析（本月 vs 去年同月）
- [ ] 环比分析（本月 vs 上月）

#### 4.4 智能洞察
- [ ] 异常消费检测（突然大额支出）
- [ ] 定期账单识别（房租、会员、订阅）
- [ ] 消费趋势预警

---

### 5. 预算管理

#### 5.1 预算设置
- [ ] 月度总预算
- [ ] 分类预算（餐饮 3000/月）
- [ ] 预算周期自定义（按周/按月）

#### 5.2 预算提醒
- [ ] 超支提醒
- [ ] 即将超支预警（已用 80%）
- [ ] 预算执行报告

#### 5.3 储蓄目标
- [ ] 目标设定（年底存 5 万）
- [ ] 进度追踪
- [ ] 自动计算每月需存金额

---

### 6. AI 能力

#### 6.1 自动分类
- [ ] 规则匹配（商户名关键词）
- [ ] AI 推断（模糊匹配）
- [ ] 用户纠正 → 持续学习

#### 6.2 智能建议
- [ ] 省钱建议
- [ ] 消费习惯洞察
- [ ] 类似用户对比（可选）

#### 6.3 退款匹配
- [ ] 退款自动关联原订单
- [ ] 净支出计算

---

### 7. 其他功能

#### 7.1 搜索与筛选
- [ ] 关键词搜索
- [ ] 时间范围筛选
- [ ] 金额范围筛选
- [ ] 分类筛选

#### 7.2 数据导出
- [ ] 导出 Excel
- [ ] 导出 PDF 报表
- [ ] 自定义导出范围

#### 7.3 分账记录
- [ ] AA 制记录
- [ ] 谁欠谁多少
- [ ] 结算提醒

#### 7.4 标签系统
- [ ] 自定义标签（旅行、项目名等）
- [ ] 按标签统计

---

## CSV 格式规范

### 支付宝账单

**文件特征：**
- 编码：GBK（需转换为 UTF-8）
- 前 24 行为头部信息（账户信息、统计摘要、提示说明）
- 第 25 行为列标题
- 第 26 行起为数据

**列字段（12列）：**

| 序号 | 字段名 | 示例 | 说明 |
|------|--------|------|------|
| 1 | 交易时间 | `2026-04-07 04:41:31` | 精确到秒 |
| 2 | 交易分类 | `日用百货` | 支付宝自带分类 |
| 3 | 交易对方 | `抖音电商商家` | 商户名称 |
| 4 | 对方账号 | `shg***@bytedance.com` | 可能为 `/` |
| 5 | 商品说明 | `抖音电商-订单编号xxx` | 交易描述 |
| 6 | 收/支 | `支出` / `收入` / `不计收支` | 交易方向 |
| 7 | 金额 | `26.90` | 数字，无货币符号 |
| 8 | 收/付款方式 | `余额宝` | 支付方式 |
| 9 | 交易状态 | `交易成功` | 状态 |
| 10 | 交易订单号 | `2026040622001404951435222512` | **唯一标识，用于去重** |
| 11 | 商家订单号 | `2001052604060103807748336836` | 商家系统订单号 |
| 12 | 备注 | 空 | 用户备注 |

**支付宝自带分类：**
- 日用百货、餐饮美食、交通出行、文化休闲
- 数码电器、美容美发、充值缴费、投资理财
- 转账红包、亲友代付、退款、保险、医疗健康 等

**去重策略：**
- 优先使用「交易订单号」（第10列）去重，这是唯一标识
- 退款记录订单号格式：`原订单号_退款订单号`，可用于关联

**特殊处理：**
- `不计收支`：余额宝收益、基金买卖、转账等，需单独处理
- `亲友代付`：亲情卡消费，实际消费者可能是家人

---

### 微信账单

**文件特征：**
- 编码：UTF-8（无需转换）
- 前 17 行为头部信息
- 第 18 行为列标题
- 第 19 行起为数据

**列字段（11列）：**

| 序号 | 字段名 | 示例 | 说明 |
|------|--------|------|------|
| 1 | 交易时间 | `2026-04-06 12:54:00` | 精确到秒 |
| 2 | 交易类型 | `商户消费` | 微信自带分类 |
| 3 | 交易对方 | `拼多多平台商户` | 人名或商户 |
| 4 | 商品 | `商户单号XP23260405...` | 描述，可能为 `/` |
| 5 | 收/支 | `支出` / `收入` / `/` | `/` 表示中性交易 |
| 6 | 金额(元) | `42.16` | 数字 |
| 7 | 支付方式 | `零钱通` | 零钱/零钱通/银行卡 |
| 8 | 当前状态 | `支付成功` | 状态 |
| 9 | 交易单号 | `4200003064202604058772879832` | **唯一标识，用于去重** |
| 10 | 商户单号 | `XP2326040500200794223082005388` | 商户系统订单号 |
| 11 | 备注 | `/` | 用户备注 |

**微信交易类型：**
- **消费类**：商户消费、亲属卡交易
- **转账类**：转账、二维码收款
- **红包类**：微信红包、微信红包（单发）、微信红包（群红包）
- **理财类**：转入零钱通-来自零钱、零钱通转出-到零钱、零钱提现
- **退款类**：微信红包-退款、转账-退款、亲属卡交易-退款
- **公益类**：分分捐

**去重策略：**
- 使用「交易单号」（第9列）去重

**特殊处理：**
- `收/支 = /`：中性交易（零钱通存取、提现等），不计入收支统计
- `亲属卡交易`：给家人绑定的亲属卡，实际消费者是家人（你的 CSV 里是 `a弟`）
- 退款记录：商户单号关联原交易

---

## 技术架构

### 架构决策
- **平台**：Web 端（响应式设计）
- **适配**：电脑 > 平板 > 手机
- **架构**：前端薄客户端 + 后端厚服务
- **数据**：云端存储，多设备访问

### 前端（Web）
- [ ] **技术选型**：Vue 3 / React / Next.js
- [ ] **UI 框架**：TailwindCSS + 组件库（Element Plus / Ant Design）
- [ ] **图表库**：ECharts / Chart.js
- [ ] **响应式断点**：
  - 桌面端 ≥1024px：完整功能，多列布局
  - 平板端 768-1024px：简化布局，图表为主
  - 手机端 <768px：单列布局，快速记账
- [ ] **PWA 支持**：可安装到桌面，离线查看

### 后端
- [ ] **技术选型**：Python（FastAPI / Django）
  - AI 集成方便，生态成熟
- [ ] **数据库**：PostgreSQL
- [ ] **云服务**：阿里云 / 腾讯云
- [ ] **职责**：
  - CSV 解析与去重
  - 数据存储与同步
  - 分类规则引擎
  - 统计分析计算
  - AI 调用与结果处理

### AI 能力
- [ ] **用途**：
  - 智能分类（商户名 → 消费类别）
  - 消费洞察（异常检测、趋势分析）
  - 月度/年度总结报告
- [ ] **方案**：规则优先 + LLM 兜底
  - 规则匹配：关键词匹配，成本为 0
  - LLM 兜底：无法匹配时调用 AI
- [ ] **模型选择**：通义千问（国内、成本低）

### 数据库设计

#### 用户与家庭

```sql
-- 用户表
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    nickname        VARCHAR(50) NOT NULL,
    avatar_url      VARCHAR(500),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- 家庭/组表（可以是家庭、朋友圈、合租等）
CREATE TABLE families (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,      -- 如：小明的家、合租小分队
    owner_id        BIGINT REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 家庭成员关系表
CREATE TABLE family_members (
    id              BIGSERIAL PRIMARY KEY,
    family_id       BIGINT REFERENCES families(id),
    user_id         BIGINT REFERENCES users(id),
    role            VARCHAR(20) DEFAULT 'member',  -- owner/admin/member
    nickname        VARCHAR(50),                   -- 在家庭中的称呼，如"老公"
    joined_at       TIMESTAMP DEFAULT NOW(),
    UNIQUE(family_id, user_id)
);

-- 邀请表
CREATE TABLE invitations (
    id              BIGSERIAL PRIMARY KEY,
    family_id       BIGINT REFERENCES families(id),
    inviter_id      BIGINT REFERENCES users(id),
    invite_code     VARCHAR(20) UNIQUE NOT NULL,
    expires_at      TIMESTAMP NOT NULL,
    used_by         BIGINT REFERENCES users(id),
    used_at         TIMESTAMP
);
```

#### 交易数据

```sql
-- 交易记录表（核心表）
CREATE TABLE transactions (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id) NOT NULL,  -- 所属用户

    -- 原始数据
    source          VARCHAR(20) NOT NULL,       -- alipay/wechat/manual
    source_order_id VARCHAR(100),               -- 原始订单号，用于去重

    -- 交易信息
    transaction_time TIMESTAMP NOT NULL,
    amount          DECIMAL(12,2) NOT NULL,
    direction       VARCHAR(10) NOT NULL,       -- income/expense/neutral
    counterparty    VARCHAR(200),               -- 交易对方
    description     TEXT,                       -- 商品说明

    -- 分类
    source_category VARCHAR(50),                -- 原始分类（来自CSV）
    category_id     BIGINT REFERENCES categories(id),  -- 系统分类

    -- 支付信息
    payment_method  VARCHAR(50),                -- 支付方式
    status          VARCHAR(50),                -- 交易状态

    -- 家庭相关
    family_member_id BIGINT REFERENCES family_members(id),  -- 实际消费者（亲情卡场景）

    -- 元数据
    note            TEXT,                       -- 用户备注
    is_hidden       BOOLEAN DEFAULT FALSE,      -- 是否隐私（仅自己可见）
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),

    -- 去重索引
    UNIQUE(user_id, source, source_order_id)
);

-- 分类表
CREATE TABLE categories (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,       -- 餐饮、交通、购物...
    icon            VARCHAR(50),                -- 图标
    color           VARCHAR(20),                -- 颜色
    parent_id       BIGINT REFERENCES categories(id),  -- 父分类（支持二级）
    is_system       BOOLEAN DEFAULT TRUE,       -- 是否系统预设
    user_id         BIGINT REFERENCES users(id) -- 自定义分类的所属用户
);

-- 标签表（用户自定义）
CREATE TABLE tags (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    name            VARCHAR(50) NOT NULL,       -- 如：旅行、项目A
    color           VARCHAR(20),
    UNIQUE(user_id, name)
);

-- 交易-标签关联
CREATE TABLE transaction_tags (
    transaction_id  BIGINT REFERENCES transactions(id),
    tag_id          BIGINT REFERENCES tags(id),
    PRIMARY KEY(transaction_id, tag_id)
);
```

#### 预算与目标

```sql
-- 预算表
CREATE TABLE budgets (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    family_id       BIGINT REFERENCES families(id),  -- 可选，家庭预算
    category_id     BIGINT REFERENCES categories(id), -- 可选，分类预算
    amount          DECIMAL(12,2) NOT NULL,
    period          VARCHAR(20) NOT NULL,       -- monthly/yearly
    start_date      DATE NOT NULL,
    end_date        DATE
);

-- 储蓄目标
CREATE TABLE savings_goals (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    family_id       BIGINT REFERENCES families(id),
    name            VARCHAR(100) NOT NULL,      -- 如：年底存5万
    target_amount   DECIMAL(12,2) NOT NULL,
    current_amount  DECIMAL(12,2) DEFAULT 0,
    deadline        DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

#### 上传记录

```sql
-- 上传记录（用于追踪导入历史）
CREATE TABLE upload_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    source          VARCHAR(20) NOT NULL,
    filename        VARCHAR(255),
    total_rows      INT,
    imported_rows   INT,
    duplicated_rows INT,
    uploaded_at     TIMESTAMP DEFAULT NOW()
);
```

### API 设计

```
# 认证
POST /api/auth/register       # 注册
POST /api/auth/login          # 登录
POST /api/auth/logout         # 登出

# 用户
GET  /api/user/profile        # 获取个人信息
PUT  /api/user/profile        # 更新个人信息

# 家庭
POST /api/families            # 创建家庭
GET  /api/families            # 我的家庭列表
GET  /api/families/:id        # 家庭详情
PUT  /api/families/:id        # 更新家庭信息
POST /api/families/:id/invite # 生成邀请链接
POST /api/families/join       # 加入家庭（通过邀请码）
DELETE /api/families/:id/members/:userId  # 移除成员

# 交易
POST /api/transactions/upload # 上传 CSV
GET  /api/transactions        # 交易列表（支持筛选：用户、家庭、时间、分类）
POST /api/transactions        # 手动记账
PUT  /api/transactions/:id    # 修改交易
DELETE /api/transactions/:id  # 删除交易

# 统计
GET  /api/statistics          # 统计概览
GET  /api/statistics/categories  # 分类统计
GET  /api/statistics/trends   # 趋势数据
GET  /api/statistics/family   # 家庭汇总（合并所有成员）

# 预算
GET  /api/budgets             # 预算列表
POST /api/budgets             # 创建预算
PUT  /api/budgets/:id         # 更新预算

# AI
GET  /api/insights            # AI 洞察
GET  /api/report/monthly      # 月度报告
GET  /api/report/yearly       # 年度报告
```

---

## 开发路线图

### Phase 1 - MVP
> 目标：跑通核心流程

- [ ] CSV 解析（支付宝 + 微信）
- [ ] 数据去重
- [ ] 基础分类（规则匹配）
- [ ] 图表展示（饼图 + 趋势图）
- [ ] 手动记账

### Phase 2 - 用户体系
> 目标：支持多设备使用

- [ ] 注册登录
- [ ] 多设备同步
- [ ] AI 分类
- [ ] 预算管理
- [ ] 周期分析

### Phase 3 - 家庭协作
> 目标：支持家庭场景

- [ ] 家庭账户
- [ ] 成员权限
- [ ] 隐私控制
- [ ] 储蓄目标
- [ ] 智能建议

### Phase 4 - 增强功能
> 目标：完善体验

- [ ] 银行卡 CSV 支持
- [ ] 分账功能
- [ ] 数据导出
- [ ] 异常检测

---

## 待讨论问题

1. **平台选择**：先做 Web 还是 App？还是小程序？
2. **数据存储**：纯云端 vs 本地优先？
3. **AI 成本**：每条记录都调 AI？还是规则优先 + AI 兜底？
4. **商业模式**：免费 + 高级功能付费？订阅制？

---

## 更新日志

| 日期 | 更新内容 |
|------|----------|
| 2024-XX-XX | 初始需求整理 |
