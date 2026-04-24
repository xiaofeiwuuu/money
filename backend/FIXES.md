# Backend 安全与代码质量修复清单

## 优先级 Top 10

- [x] **P1**: CORS 重做 - 读取 .env 的 CORS_ORIGINS，修复 allow_credentials
- [x] **P2**: /upload 加认证 + 文件大小限制
- [x] **P3**: admin 权限检查 + transactions 的 total 改真实 COUNT
- [x] **P4**: PATCH/PUT 参数放进 Body（敏感数据不能进 URL）
- [x] **P5**: 迁移加 server_default、env.py 补 ParserConfig import
- [x] **P6**: 批量插入优化 + 出错 rollback + 记录 error_details
- [x] **P7**: bcrypt 放 threadpool 避免阻塞事件循环
- [x] **P8**: 注册 race condition 改成 catch IntegrityError
- [x] **P9**: 金额用 Decimal 字符串传输
- [x] **P10**: run.py 区分 dev/prod

## 其他问题

- [x] N5: app/models 目录不存在（使用 schemas 目录，已有 __init__.py）
- [x] N11: /transactions total 字段 - 已改为真实 COUNT
- [x] N13: end_date 日期截止问题 - 已改为 < end_date + 1 day
- [x] N15: 两次 commit 破坏原子性 - 合并为单次 commit
- [x] N18: Family.invite_code 生成逻辑 - 添加 generate_invite_code()
- [x] N20: Enum 跨层 - 迁移 005 改为 PostgreSQL Enum 类型
- [x] N21: /health 检查数据库 - 添加 SELECT 1 + 状态返回
- [x] N22: 日志配置 - 添加 logging.basicConfig
- [x] N27: Pydantic v2 ConfigDict 语法 - 已修复
- [x] datetime.utcnow 全部替换为 utcnow() (timezone aware)

## 第二轮修复 (Bug 修复)

- [x] B1: load_parser_config 合并语义 - DB 覆盖默认值，非替换
- [x] B2: 批量插入 fallback 需要 rollback - 添加 await db.rollback()
- [x] B3: transaction_time 时区统一 - 改为 DateTime(timezone=True)
- [x] B4: stats 日期边界一致 - 统一使用 < end_date + 1 day
- [x] B5: migration server_default - 创建 006_fix_nullability.py
- [x] B6/B7: 死代码清理 + 缓存返回副本
- [x] B8: unknown 死代码移除
- [x] B9: Enum 合并 - schemas 导入 db.models 的 Enum
- [x] B10: migration f-string SQL - 002/003 改用 bulk_insert
- [x] B11: DEBUG SECRET_KEY 持久化 - 使用固定开发密钥
- [x] B14: StatsResponse 精度统一 - 改为 str
- [x] B15: stats 3 次查询合并为 1 次（使用 CASE WHEN）
- [x] B16/B17: 大文件性能优化 - iterrows 改为 itertuples
- [x] B19: 关键路径添加日志 - upload/save 异常记录

## 第三轮修复

- [x] N1: 时区偏差 8 小时 - parse_datetime 添加 Asia/Shanghai 时区
- [x] N2: fallback rollback 撤销成功数据 - 改用 savepoint (begin_nested)
- [x] N3: itertuples 性能优化未生效 - 预计算索引，直接按索引取值
- [x] N7: 函数内 import - 移至模块顶层
- [x] N8: 未使用导入 get_default_aliases - 已删除
- [x] N11: upload.py source fallback 死代码 - 已简化
- [x] N16: 文件名进日志隐私问题 - 改为只记 user_id
