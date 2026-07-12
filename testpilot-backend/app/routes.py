"""API 路由：3 个核心接口 + 健康检查"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from .config import get_settings
from .models import (
    AnalyzeRequest,
    AnalyzeResponse,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    RunRequest,
    RunResponse,
)
from .services import AIService, ExecutionService

router = APIRouter(prefix="/api", tags=["testpilot"])

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """健康检查"""
    s = get_settings()
    return HealthResponse(status="ok", has_api_key=s.has_api_key)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """需求分析：需求文本 → 功能点列表"""
    ai = AIService()
    try:
        logger.debug(f"Analyzing requirement: {req.requirement_text[:100]}...")
        logger.debug(f"App URL: {req.app_url}")
        result = await ai.analyze_requirement(req.requirement_text, req.app_url)
        logger.debug(f"Analysis completed: {len(result.feature_points)} feature points")
        return result
    except RuntimeError as e:
        logger.error(f"Runtime error in analyze: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in analyze: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"需求分析失败: {type(e).__name__}: {e}")


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest) -> GenerateResponse:
    """脚本生成：功能点 → Playwright 脚本"""
    ai = AIService()
    try:
        return await ai.generate_scripts(req.feature_points, req.app_url)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脚本生成失败: {e}")


@router.post("/run", response_model=RunResponse)
async def run(req: RunRequest) -> RunResponse:
    """脚本执行：脚本 → 执行结果"""
    executor = ExecutionService()
    try:
        return await executor.run_script(req.script, req.app_url, req.timeout)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脚本执行失败: {e}")
