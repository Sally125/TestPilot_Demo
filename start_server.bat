@echo off
echo ==============================================
echo    TestPilot AI 测试智能体 - 后端服务启动脚本
echo ==============================================
echo.

cd /d "%~dp0testpilot-backend"

echo 正在检查 Python 环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo.
echo 正在启动后端服务...
echo 服务地址: http://localhost:8000
echo Swagger 文档: http://localhost:8000/docs
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause