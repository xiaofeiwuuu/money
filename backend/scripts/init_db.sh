#!/bin/bash
# 初始化数据库脚本

set -e

echo "启动 PostgreSQL..."
cd "$(dirname "$0")/../.."
docker-compose up -d db

echo "等待数据库就绪..."
sleep 3

echo "运行数据库迁移..."
cd backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -q
alembic upgrade head

echo "数据库初始化完成！"
