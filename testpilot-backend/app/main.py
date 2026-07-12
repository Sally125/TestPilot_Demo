"""FastAPI 主应用"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routes import router
from .database import engine
from . import db_models

db_models.Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title="TestPilot AI 测试智能体",
    description=(
        "AI 驱动的自动化测试生成服务 —— "
        "需求分析 → Playwright 脚本生成 → 脚本执行"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/screenshots", StaticFiles(directory=settings.runtime_dir), name="screenshots")

# CORS：允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Day 1 阶段先放开，后续按需收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root() -> dict:
    """根路径：返回服务信息"""
    return {
        "name": "TestPilot AI 测试智能体",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "analyze": "POST /api/analyze — 需求文本 → 功能点列表",
            "generate": "POST /api/generate — 功能点 → Playwright 脚本",
            "run": "POST /api/run — 脚本 → 执行结果",
            "health": "GET /api/health — 健康检查",
        },
        "has_api_key": settings.has_api_key,
    }
