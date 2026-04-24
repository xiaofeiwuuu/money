# Money Manager - 项目说明

## 项目概述

个人/家庭收支管理系统，支持支付宝、微信账单 CSV/XLSX 导入，提供数据去重、统计分析等功能。

---

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.12+ | 主语言 |
| **FastAPI** | 0.100+ | Web 框架 |
| **SQLAlchemy** | 2.0+ | ORM (异步) |
| **PostgreSQL** | 15+ | 数据库 |
| **asyncpg** | 0.28+ | 异步 PostgreSQL 驱动 |
| **Alembic** | 1.11+ | 数据库迁移 |
| **Pydantic** | 2.0+ | 数据验证 |
| **bcrypt** | 4.0+ | 密码哈希 |
| **python-jose** | 3.3+ | JWT 认证 |
| **pandas** | 2.0+ | CSV 解析 |
| **openpyxl** | 3.1+ | XLSX 解析 |

### 开发工具

| 工具 | 用途 |
|------|------|
| **pre-commit** | Git hooks (Ruff, Bandit, Vulture) |
| **pytest** | 单元测试 |
| **pytest-asyncio** | 异步测试支持 |
| **GitHub Actions** | CI/CD |

---

## 项目结构

```
backend/
├── app/
│   ├── api/                # API 路由
│   │   ├── auth.py         # 认证 (注册/登录)
│   │   ├── upload.py       # 文件上传
│   │   ├── transactions.py # 交易 CRUD
│   │   └── admin.py        # 管理接口
│   ├── core/               # 核心配置
│   │   ├── config.py       # 环境配置 (Pydantic Settings)
│   │   ├── database.py     # 数据库连接
│   │   └── security.py     # JWT + 密码处理
│   ├── db/
│   │   └── models.py       # SQLAlchemy 模型
│   ├── parsers/            # CSV/XLSX 解析器
│   │   ├── base.py         # 解析器基类
│   │   ├── alipay.py       # 支付宝解析
│   │   ├── wechat.py       # 微信解析
│   │   ├── parser.py       # 解析器调度
│   │   └── config.py       # 列名别名配置
│   ├── schemas/
│   │   └── transaction.py  # Pydantic 模型
│   └── services/
│       ├── transaction.py  # 交易业务逻辑
│       └── parser_config.py# 配置加载
├── alembic/                # 数据库迁移
│   └── versions/           # 6 个迁移文件
├── tests/                  # 测试 (22 个用例)
│   ├── test_parsers.py
│   ├── test_security.py
│   └── test_timezone.py
├── .github/workflows/
│   └── ci.yml              # GitHub Actions CI
└── requirements.txt
```

---

## 已完成功能

### 认证系统
- [x] 用户注册 (邮箱 + 密码)
- [x] 用户登录 (JWT Token)
- [x] 密码哈希 (bcrypt, 异步线程池)
- [x] Race condition 防护 (IntegrityError 捕获)
- [x] 账号枚举防护 (统一登录失败消息)

### 文件上传
- [x] 支付宝 CSV 解析 (GBK 编码)
- [x] 微信 XLSX 解析
- [x] 自动表头检测 (跳过前 N 行)
- [x] 自动编码检测 (UTF-8/GBK/GB2312)
- [x] 文件大小限制 (20MB)
- [x] 需登录才能上传

### 数据处理
- [x] 批量插入 (SQLAlchemy bulk_insert)
- [x] 自动去重 (source + order_id 唯一索引)
- [x] 失败回滚 (Savepoint 保护)
- [x] 金额精度保证 (Decimal 字符串传输)
- [x] 时区处理 (北京时间 UTC+8)

### 交易查询
- [x] 分页查询
- [x] 日期范围筛选
- [x] 收支方向筛选
- [x] 统计汇总 (收入/支出/余额)
- [x] 交易更新 (备注、隐藏)

### 管理功能
- [x] 解析器配置管理 (列名别名)
- [x] 管理员权限检查
- [x] 配置热重载

### 安全特性
- [x] CORS 配置 (从环境变量读取)
- [x] JWT 过期时间
- [x] 敏感数据不进 URL (PATCH Body)
- [x] 数据库连接检查 (/health)
- [x] 日志记录 (关键操作)

---

## 数据库模型

| 模型 | 说明 |
|------|------|
| `User` | 用户 (邮箱、密码、昵称、管理员标识) |
| `Family` | 家庭 (名称、邀请码) |
| `FamilyMember` | 家庭成员关系 |
| `Category` | 分类 (预设 + 自定义) |
| `TransactionRecord` | 交易记录 (核心表) |
| `ParserConfig` | 解析器配置 (列名别名) |
| `UploadLog` | 上传日志 |

---

## API 端点

```
认证
  POST /api/auth/register    # 注册
  POST /api/auth/login       # 登录

上传
  POST /api/upload           # 解析预览
  POST /api/upload/save      # 解析并保存
  POST /api/upload/preview   # 快速预览

交易
  GET  /api/transactions       # 列表 (分页+筛选)
  GET  /api/transactions/stats # 统计
  PATCH /api/transactions/:id  # 更新

管理 (需管理员)
  GET  /api/admin/parser-config      # 获取配置
  PUT  /api/admin/parser-config      # 更新配置
  POST /api/admin/parser-config/alias# 添加别名
  POST /api/admin/reload-config      # 重载配置

系统
  GET  /                # 版本信息
  GET  /health          # 健康检查 (含数据库)
```

---

## 测试覆盖

| 测试文件 | 用例数 | 覆盖内容 |
|----------|--------|----------|
| `test_parsers.py` | 8 | 解析器、编码检测、表头检测 |
| `test_security.py` | 5 | 密码哈希、JWT 创建/验证 |
| `test_timezone.py` | 9 | 时区处理、日期解析 |
| **合计** | **22** | |

---

## CI/CD

GitHub Actions 配置:
- Python 版本矩阵: 3.12, 3.13
- PostgreSQL 15 服务容器
- pre-commit 检查 (Ruff, Bandit, Vulture)
- Alembic 迁移
- pytest 测试

---

## 环境变量

```bash
# 必需
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/money
SECRET_KEY=your-secret-key

# 可选
DEBUG=true                    # 开发模式
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 快速开始

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env  # 编辑配置

# 5. 运行迁移
alembic upgrade head

# 6. 启动服务
python run.py  # 或 uvicorn app.main:app --reload
```

---

## 代码质量

已完成 5 轮代码审查和修复:

| 轮次 | 修复项 |
|------|--------|
| 第一轮 (P1-P10) | CORS、认证、权限、参数安全、bcrypt 异步 |
| 第二轮 (B1-B19) | 配置合并、时区、迁移、性能优化 |
| 第三轮 (N1-N16) | 时区偏差、Savepoint、itertuples 优化 |
| 第四轮 (P0-P3, C1-C3) | CI/CD、时区测试、日志完善 |
| 第五轮 (L1-L2) | preview_upload 日志、OpenAPI 类型 |

详见 [backend/FIXES.md](backend/FIXES.md)

---

## 待开发功能

- [ ] 前端 (Vue 3 / React)
- [ ] 银行卡 CSV 支持
- [ ] 手动记账
- [ ] 预算管理
- [ ] 家庭协作
- [ ] AI 智能分类
- [ ] 数据导出

---

*最后更新: 2026-04-24*
