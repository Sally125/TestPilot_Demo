#!/usr/bin/env bash
# TestPilot 后端服务启动脚本

set -e

cd "$(dirname "$0")"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "[警告] 未找到 .env 文件，正在从 .env.example 创建..."
    cp .env.example .env
    echo "[提示] 请编辑 .env 文件，填入 DEEPSEEK_API_KEY"
fi

# 检查依赖
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "[安装] 正在安装依赖..."
    pip install -r requirements.txt --break-system-packages
fi

# 读取端口
PORT=$(grep "^APP_PORT=" .env | cut -d'=' -f2 || echo "8000")
PORT=${PORT:-8000}

echo "[启动] TestPilot 后端服务，端口: $PORT"
echo "[文档] API 文档: http://localhost:$PORT/docs"
echo ""

exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
