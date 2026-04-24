#!/usr/bin/env python3
"""启动服务器（仅用于开发）

生产环境请使用:
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
"""

import os

import uvicorn

if __name__ == "__main__":
    debug = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    if debug:
        # 开发模式：localhost + 自动重载
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",  # 仅本地访问
            port=8000,
            reload=True,
        )
    else:
        # 非开发模式警告
        print("WARNING: run.py 仅用于开发。生产环境请使用 gunicorn。")
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
        )
