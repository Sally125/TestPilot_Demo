"""API 路由：3 个核心接口 + 健康检查 + 项目管理"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session

from .config import get_settings
from .models import (
    AnalyzeRequest,
    AnalyzeResponse,
    DesignTestCasesRequest,
    DesignTestCasesResponse,
    FeaturePoint,
    GenerateRequest,
    GenerateResponse,
    GeneratedCase,
    HealthResponse,
    RunRequest,
    RunResponse,
    ReviewRequest,
    ReviewResponse,
    ProjectCreate,
    ProjectResponse,
    LoginStateStatus,
    RequirementCreate,
    AnalysisSaveRequest,
    TestCaseCreate,
    TestCaseStatusUpdate,
    ExecutionRecordCreate,
    ExecutionCreate,
    ExecutionUpdate,
    TestReportCreate,
    SettingSaveRequest,
    LoginProfileCreate,
    LoginProfileUpdate,
    SuggestionStatusUpdate,
    CaseUpdateRequest,
)
from .services import AIService, ExecutionService
from .session_generator import LoginSessionGenerator
from .stability_checker import StabilityChecker
from .prompts import ANALYZE_PROMPT
from .database import get_db
from .db_models import TestCase
from .crud import (
    get_projects,
    get_project,
    get_project_by_name,
    get_project_login_state_status,
    create_project,
    update_project,
    delete_project,
    create_requirement,
    get_requirements,
    get_requirement,
    update_requirement_analysis,
    delete_requirement,
    create_test_case,
    get_test_cases,
    update_test_case_status,
    delete_test_case,
    create_execution_record,
    get_execution_records,
    add_execution_log,
    create_stability_report,
    get_stability_report,
    create_review_report,
    get_review_report,
    get_review_report_by_id,
    create_review_suggestion,
    get_suggestions_by_review,
    get_suggestion_by_uid,
    get_suggestions_by_case,
    update_suggestion_status,
    update_test_case_review_status,
    update_case_with_suggestion,
    create_execution,
    update_execution,
    get_execution,
    get_executions,
    delete_execution,
    create_test_report,
    get_test_report,
    get_setting,
    set_setting,
    get_settings_by_category,
    get_all_settings,
    get_login_profiles,
    get_login_profile,
    get_default_login_profile,
    count_login_profiles,
    create_login_profile,
    update_login_profile,
    delete_login_profile,
)

router = APIRouter(prefix="/api", tags=["testpilot"])

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    s = get_settings()
    return HealthResponse(status="ok", has_api_key=s.has_api_key)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
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


@router.post("/analyze/stream")
async def analyze_stream(req: AnalyzeRequest):
    from fastapi.responses import StreamingResponse
    import json
    import asyncio
    
    ai = AIService()
    
    async def generate():
        try:
            logger.debug(f"Analyzing requirement (stream): {req.requirement_text[:100]}...")
            
            yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': 'AI正在思考中...'})}\n\n"
            await asyncio.sleep(0.01)
            
            prompt = ANALYZE_PROMPT.format(
                requirement_text=req.requirement_text,
                app_url=req.app_url or "未提供",
            )
            
            buffer = ""
            chunk_count = 0
            async for chunk in ai.chat_stream(prompt):
                buffer += chunk
                chunk_count += 1
                yield f"data: {json.dumps({'type': 'progress', 'content': chunk, 'buffer_length': len(buffer)})}\n\n"
                if chunk_count % 5 == 0:
                    await asyncio.sleep(0.001)
            
            text = buffer.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            
            try:
                data = json.loads(text)
                feature_points = []
                for fp in data.get("feature_points", []):
                    test_dims = fp.get("test_dimensions", [])
                    if isinstance(test_dims, str):
                        test_dims = [d.strip() for d in test_dims.split() if d.strip()]
                    elif not isinstance(test_dims, list):
                        test_dims = []
                    
                    feature_points.append({
                        "name": fp.get("name", "未命名功能"),
                        "priority": fp.get("priority", "P2"),
                        "test_dimensions": test_dims,
                        "business_logic": fp.get("business_logic", ""),
                        "risk_hint": fp.get("risk_hint", ""),
                    })
                
                result = {
                    "type": "complete",
                    "feature_points": feature_points,
                    "summary": data.get("summary", ""),
                    "estimated_case_count": data.get("estimated_case_count", len(feature_points) * 3),
                    "raw": text,
                }
                yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
                logger.debug("Analyze stream completed, yielding done event")
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}, raw: {text[:500]}")
                yield f"data: {json.dumps({'type': 'error', 'message': f'JSON 解析失败: {str(e)}', 'raw': buffer[:500]})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            logger.error(f"Unexpected error in analyze stream: {type(e).__name__}: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': f'需求分析失败: {type(e).__name__}: {str(e)}'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked",
        },
    )


@router.post("/design-testcases", response_model=DesignTestCasesResponse)
async def design_testcases(req: DesignTestCasesRequest) -> DesignTestCasesResponse:
    ai = AIService()
    try:
        return await ai.design_test_cases(req.feature_points)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试用例设计失败: {e}")


@router.post("/design-testcases/stream")
async def design_testcases_stream(req: DesignTestCasesRequest):
    from fastapi.responses import StreamingResponse
    import json
    import asyncio
    
    ai = AIService()
    
    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': 'AI正在设计测试用例...'})}\n\n"
            await asyncio.sleep(0.01)
            
            fp_json = json.dumps(
                [{"id": f"FP-{i+1:03d}", **fp.model_dump()} for i, fp in enumerate(req.feature_points)],
                ensure_ascii=False, indent=2
            )
            from datetime import datetime
            generation_time = datetime.now().isoformat()
            
            from .prompts import TESTCASE_DESIGN_PROMPT_PART1, TESTCASE_DESIGN_PROMPT_PART2, TESTCASE_DESIGN_PROMPT_JSON_TEMPLATE
            prompt = TESTCASE_DESIGN_PROMPT_PART1 + TESTCASE_DESIGN_PROMPT_JSON_TEMPLATE + TESTCASE_DESIGN_PROMPT_PART2.format(
                feature_points_json=fp_json,
            )
            
            buffer = ""
            async for chunk in ai.chat_stream(prompt):
                buffer += chunk
                yield f"data: {json.dumps({'type': 'progress', 'content': chunk, 'buffer_length': len(buffer)})}\n\n"
            
            text = buffer.strip()
            
            if not text:
                yield f"data: {json.dumps({'type': 'error', 'message': 'AI返回内容为空，请检查API Key和网络连接', 'raw': ''})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
            
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            
            try:
                data = json.loads(text)
                result_dict = {
                    "type": "complete",
                    "testcase_summary": data.get("testcase_summary", {}),
                    "test_cases": data.get("test_cases", []),
                    "coverage_matrix": data.get("coverage_matrix", {}),
                    "raw": text,
                }
                yield f"data: {json.dumps(result_dict, ensure_ascii=False)}\n\n"
            except json.JSONDecodeError as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'JSON解析失败: {str(e)}', 'raw': buffer[:500]})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'测试用例设计失败: {type(e).__name__}: {str(e)}'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked",
        },
    )


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, db: Session = Depends(get_db)) -> GenerateResponse:
    import datetime
    
    storage_state_path = None
    if req.project_id:
        project = get_project(db, req.project_id)
        if project and getattr(project, 'requires_login', 1) == 1:
            default_profile = get_default_login_profile(db, req.project_id)
            if not default_profile or not default_profile.storage_state_path:
                raise HTTPException(
                    status_code=400,
                    detail="项目需要登录态，但尚未生成会话。请先在「登录态配置」中生成会话后再生成脚本。"
                )
            if default_profile.valid_until:
                now = datetime.datetime.now(datetime.timezone.utc)
                valid_until_utc = default_profile.valid_until.astimezone(datetime.timezone.utc) if default_profile.valid_until.tzinfo else default_profile.valid_until.replace(tzinfo=datetime.timezone.utc)
                if valid_until_utc < now:
                    raise HTTPException(
                        status_code=400,
                        detail="项目登录态会话已过期，请重新生成会话后再生成脚本。"
                    )
            storage_state_path = default_profile.storage_state_path

    ai = AIService()
    try:
        print(f"[DEBUG] /generate - test_cases count: {len(req.test_cases)}")
        if req.test_cases:
            print(f"[DEBUG] /generate - first test_case: {req.test_cases[0].id} - {req.test_cases[0].title[:50]}")
        print(f"[DEBUG] /generate - app_url: {req.app_url}")
        print(f"[DEBUG] /generate - storage_state_path: {storage_state_path}")
        return await ai.generate_scripts(req.test_cases, req.app_url, storage_state_path)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脚本生成失败: {e}")


@router.post("/generate/stream")
async def generate_stream(req: GenerateRequest, db: Session = Depends(get_db)):
    from fastapi.responses import StreamingResponse
    import json
    import asyncio
    import datetime
    
    storage_state_path = None
    if req.project_id:
        project = get_project(db, req.project_id)
        if project and getattr(project, 'requires_login', 1) == 1:
            default_profile = get_default_login_profile(db, req.project_id)
            if not default_profile or not default_profile.storage_state_path:
                raise HTTPException(
                    status_code=400,
                    detail="项目需要登录态，但尚未生成会话。请先在「登录态配置」中生成会话后再生成脚本。"
                )
            if default_profile.valid_until:
                now = datetime.datetime.now(datetime.timezone.utc)
                valid_until_utc = default_profile.valid_until.astimezone(datetime.timezone.utc) if default_profile.valid_until.tzinfo else default_profile.valid_until.replace(tzinfo=datetime.timezone.utc)
                if valid_until_utc < now:
                    raise HTTPException(
                        status_code=400,
                        detail="项目登录态会话已过期，请重新生成会话后再生成脚本。"
                    )
            storage_state_path = default_profile.storage_state_path
    
    ai = AIService()
    
    async def generate():
        try:
            total_cases = len(req.test_cases)
            yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': f'AI正在生成测试脚本... ({total_cases}条用例)'})}\n\n"
            await asyncio.sleep(0.01)
            
            try:
                cases = []
                raw = ""
                
                yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': '正在准备生成所有脚本...'})}\n\n"
                await asyncio.sleep(0.1)
                
                tc_json = json.dumps([tc.model_dump() for tc in req.test_cases], ensure_ascii=False, indent=2)
                
                s = ai.settings
                test_account = "未提供"
                if s.test_username:
                    test_account = f"用户名: {s.test_username} / 密码: {s.test_password or '***'}"
                
                app_name = "应用系统"
                modules = set()
                for tc_item in req.test_cases:
                    if tc_item.module:
                        modules.add(tc_item.module)
                if modules:
                    app_name = ", ".join(list(modules)[:3])
                
                from .prompts import GENERATE_PROMPT
                base_prompt = GENERATE_PROMPT.format(
                    test_cases_json=tc_json,
                    app_name=app_name,
                    app_url=req.app_url or "未提供",
                    login_url=s.login_url or "未提供",
                    test_account=test_account,
                    test_username=s.test_username or "",
                    test_password=s.test_password or "",
                    page_context="# 页面快照（暂未启用）",
                )
                
                yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': f'正在调用AI生成{total_cases}条脚本...'})}\n\n"
                await asyncio.sleep(0.1)
                
                tc_raw = await ai.chat(base_prompt)
                raw += tc_raw + "\n"
                
                yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': 'AI响应完成，正在解析...'})}\n\n"
                await asyncio.sleep(0.1)
                
                try:
                    data = ai._parse_json(tc_raw)
                    scripts = data.get("scripts", [])
                    if scripts:
                        from .stability_checker import StabilityChecker
                        checker = StabilityChecker()
                        
                        for i, c in enumerate(scripts):
                            tc = req.test_cases[i] if i < len(req.test_cases) else None
                            script = ai._strip_code_fence(c.get("script", ""))
                            
                            yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': f'正在进行稳定性检测 ({i+1}/{len(scripts)})...'})}\n\n"
                            await asyncio.sleep(0.1)
                            
                            stability_check_result = checker.analyze(script, c.get("case_title", tc.title if tc else ""))
                            
                            cases.append({
                                "title": c.get("case_title", tc.title if tc else ""),
                                "module": c.get("module", tc.module or "" if tc else ""),
                                "priority": c.get("priority", tc.priority if tc else "P1"),
                                "precondition": "",
                                "steps": [],
                                "expected": "",
                                "script": script,
                                "stability_score": stability_check_result.get("overall_score", 80),
                                "stability_checks": stability_check_result.get("checks"),
                                "stability_issues": stability_check_result.get("issues", []),
                            })
                            
                            score = stability_check_result.get("overall_score", 80)
                            msg = f"稳定性检测完成，得分{score}"
                            yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': msg})}\n\n"
                            await asyncio.sleep(0.1)
                    else:
                        yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': '未生成任何脚本'})}\n\n"
                        await asyncio.sleep(0.1)
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'progress', 'content': '', 'buffer_length': 0, 'message': f'脚本解析失败 - {str(e)}'})}\n\n"
                    await asyncio.sleep(0.1)
                
                result_dict = {
                    "type": "complete",
                    "cases": cases,
                    "raw": raw,
                }
                yield f"data: {json.dumps(result_dict, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'脚本生成失败: {type(e).__name__}: {str(e)}'})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'脚本生成失败: {type(e).__name__}: {str(e)}'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked",
        },
    )


@router.post("/run", response_model=RunResponse)
async def run(req: RunRequest) -> RunResponse:
    executor = ExecutionService()
    try:
        return await executor.run_script(req.script, req.app_url, req.timeout, req.storage_state_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脚本执行失败: {e}")


# ==================== 质量评审 ====================

@router.post("/review", response_model=ReviewResponse)
async def review(req: ReviewRequest) -> ReviewResponse:
    ai = AIService()
    try:
        logger.debug(f"Reviewing {len(req.cases)} cases against {len(req.feature_points)} feature points")
        result = await ai.review_cases(req.cases, req.feature_points)
        logger.debug(f"Review completed: overall_score={result.overall_score}, suggestions={len(result.suggestions)}")
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in review: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"质量评审失败: {type(e).__name__}: {e}")


# ==================== 项目管理 ====================

@router.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    projects = get_projects(db)
    results = []
    for p in projects:
        login_state_status = get_project_login_state_status(db, p.id)
        results.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "appUrl": p.app_url,
            "dim": p.dim,
            "techStack": p.tech_stack,
            "requiresLogin": getattr(p, 'requires_login', 1),
            "loginStateStatus": login_state_status,
            "createdAt": p.created_at,
            "updatedAt": p.updated_at
        })
    return results


@router.post("/projects")
async def add_project(
    req: ProjectCreate,
    db: Session = Depends(get_db)
):
    existing = get_project_by_name(db, req.name)
    if existing:
        raise HTTPException(status_code=400, detail="项目名称已存在")
    
    project = create_project(db, req.name, req.description, req.appUrl, req.dim, req.techStack, req.requiresLogin)
    if not project:
        raise HTTPException(status_code=400, detail="创建项目失败")
    
    login_state_status = get_project_login_state_status(db, project.id)
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "appUrl": project.app_url,
        "dim": project.dim,
        "techStack": project.tech_stack,
        "requiresLogin": project.requires_login,
        "loginStateStatus": login_state_status,
        "createdAt": project.created_at
    }


@router.get("/projects/{project_id}")
async def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    login_state_status = get_project_login_state_status(db, project_id)
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "appUrl": project.app_url,
        "dim": project.dim,
        "techStack": project.tech_stack,
        "requiresLogin": getattr(project, 'requires_login', 1),
        "loginStateStatus": login_state_status,
        "createdAt": project.created_at,
        "updatedAt": project.updated_at
    }


@router.put("/projects/{project_id}")
async def update_project_detail(
    project_id: int,
    name: Optional[str] = Body(default=None),
    description: Optional[str] = Body(default=None),
    appUrl: Optional[str] = Body(default=None),
    dim: Optional[str] = Body(default=None),
    techStack: Optional[str] = Body(default=None),
    requiresLogin: Optional[int] = Body(default=None),
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if appUrl is not None:
        update_data["app_url"] = appUrl
    if dim is not None:
        update_data["dim"] = dim
    if techStack is not None:
        update_data["tech_stack"] = techStack
    if requiresLogin is not None:
        update_data["requires_login"] = requiresLogin
    
    updated = update_project(db, project_id, **update_data)
    
    login_state_status = get_project_login_state_status(db, project_id)
    
    return {
        "id": updated.id,
        "name": updated.name,
        "description": updated.description,
        "appUrl": updated.app_url,
        "dim": updated.dim,
        "techStack": updated.tech_stack,
        "requiresLogin": getattr(updated, 'requires_login', 1),
        "loginStateStatus": login_state_status,
        "updatedAt": updated.updated_at
    }


@router.delete("/projects/{project_id}")
async def remove_project(project_id: int, db: Session = Depends(get_db)):
    success = delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {"success": True, "message": "项目已删除"}


# ==================== 需求管理 ====================

@router.get("/projects/{project_id}/requirements")
async def list_requirements(project_id: int, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    requirements = get_requirements(db, project_id)
    return [
        {
            "id": r.id,
            "projectId": r.project_id,
            "title": r.title,
            "content": r.content,
            "analysisResult": r.analysis_result,
            "createdAt": r.created_at
        }
        for r in requirements
    ]


@router.post("/projects/{project_id}/requirements")
async def add_requirement(
    project_id: int,
    req: RequirementCreate,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    requirement = create_requirement(db, project_id, req.title, req.content)
    return {
        "id": requirement.id,
        "projectId": requirement.project_id,
        "title": requirement.title,
        "content": requirement.content,
        "createdAt": requirement.created_at
    }


@router.get("/requirements/{req_id}")
async def get_requirement_detail(req_id: int, db: Session = Depends(get_db)):
    req = get_requirement(db, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="需求不存在")
    
    return {
        "id": req.id,
        "projectId": req.project_id,
        "title": req.title,
        "content": req.content,
        "analysisResult": req.analysis_result,
        "createdAt": req.created_at
    }


@router.put("/requirements/{req_id}/analysis")
async def save_analysis(
    req_id: int,
    body: AnalysisSaveRequest,
    db: Session = Depends(get_db)
):
    req = get_requirement(db, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="需求不存在")

    updated = update_requirement_analysis(db, req_id, body.analysis_result)
    return {
        "id": updated.id,
        "analysisResult": updated.analysis_result
    }


@router.delete("/requirements/{req_id}")
async def remove_requirement(req_id: int, db: Session = Depends(get_db)):
    success = delete_requirement(db, req_id)
    if not success:
        raise HTTPException(status_code=404, detail="需求不存在")
    return {"success": True, "message": "需求已删除"}


# ==================== 测试用例管理 ====================

@router.get("/projects/{project_id}/testcases")
async def list_test_cases(
    project_id: int,
    module: str = None,
    priority: str = None,
    status: str = None,
    keyword: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    cases, total = get_test_cases(db, project_id, module, priority, status, keyword, page, page_size)
    
    all_cases = get_test_cases(db, project_id)[0]
    module_list = list(set([c.module for c in all_cases if c.module]))
    
    return {
        "items": [
            {
                "id": c.id,
                "projectId": c.project_id,
                "requirementId": c.requirement_id,
                "title": c.title,
                "module": c.module,
                "priority": c.priority,
                "precondition": c.precondition,
                "steps": c.steps,
                "expected": c.expected,
                "script": c.script,
                "scriptPath": c.script_path,
                "status": c.status,
                "createdAt": c.created_at,
                "updatedAt": c.updated_at,
                "stabilityScore": getattr(c, 'stability_score', 0) or 0,
                "loginMode": getattr(c, 'login_mode', 'global') or 'global',
                "loginRole": getattr(c, 'login_role', None),
                "version": getattr(c, 'version', 1) or 1,
            }
            for c in cases
        ],
        "total": total,
        "page": page,
        "pageSize": page_size,
        "modules": module_list
    }


@router.post("/projects/{project_id}/testcases")
async def add_test_case(
    project_id: int,
    body: TestCaseCreate,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    case = create_test_case(
        db, project_id, body.title, body.module, body.priority, body.precondition,
        body.steps, body.expected, body.script, body.scriptPath, body.requirementId,
        body.loginMode, body.loginRole, body.stabilityScore
    )
    return {
        "id": case.id,
        "title": case.title,
        "status": case.status,
        "createdAt": case.created_at,
        "loginMode": case.login_mode,
        "loginRole": case.login_role
    }


@router.put("/testcases/{case_id}/status")
async def set_case_status(
    case_id: int,
    body: TestCaseStatusUpdate,
    db: Session = Depends(get_db)
):
    updated = update_test_case_status(db, case_id, body.status)
    if not updated:
        raise HTTPException(status_code=404, detail="用例不存在")
    return {"id": updated.id, "status": updated.status}


@router.put("/testcases/{case_id}/login")
async def update_case_login(
    case_id: int,
    body: dict,
    db: Session = Depends(get_db)
):
    """更新用例的登录态绑定"""
    login_mode = body.get("loginMode")
    login_role = body.get("loginRole")
    if login_mode not in ("global", "specified", "anonymous"):
        raise HTTPException(status_code=400, detail="loginMode 必须是 global/specified/anonymous")
    from .crud import update_test_case_login
    updated = update_test_case_login(db, case_id, login_mode, login_role)
    if not updated:
        raise HTTPException(status_code=404, detail="用例不存在")
    return {
        "id": updated.id,
        "loginMode": updated.login_mode,
        "loginRole": updated.login_role
    }


# ==================== 执行记录 ====================

@router.post("/execution-records")
async def log_execution(
    body: ExecutionRecordCreate,
    db: Session = Depends(get_db)
):
    record = create_execution_record(db, body.project_id, body.case_id, body.passed, body.duration_ms, body.error, body.screenshots)
    return {
        "id": record.id,
        "passed": bool(record.passed),
        "executedAt": record.executed_at
    }


@router.get("/projects/{project_id}/execution-records")
async def list_execution_records(project_id: int, db: Session = Depends(get_db)):
    records = get_execution_records(db, project_id=project_id)
    return [
        {
            "id": r.id,
            "projectId": r.project_id,
            "caseId": r.case_id,
            "passed": bool(r.passed),
            "durationMs": r.duration_ms,
            "error": r.error,
            "screenshots": r.screenshots,
            "executedAt": r.executed_at
        }
        for r in records
    ]


@router.delete("/testcases/{case_id}")
async def remove_test_case(case_id: int, db: Session = Depends(get_db)):
    success = delete_test_case(db, case_id)
    if not success:
        raise HTTPException(status_code=404, detail="用例不存在")
    return {"success": True, "message": "用例已删除"}


# ==================== 稳定性报告 ====================

@router.get("/projects/{project_id}/stability")
async def get_project_stability(project_id: int, db: Session = Depends(get_db)):
    report = get_stability_report(db, project_id)
    if not report:
        return {"score": 0, "checks": [], "issues": [], "scores": {}}
    return {
        "id": report.id,
        "projectId": report.project_id,
        "overallScore": report.overall_score,
        "checks": report.checks,
        "issues": report.issues,
        "scores": report.scores,
        "generatedAt": report.generated_at
    }


@router.post("/projects/{project_id}/stability")
async def save_stability_report(
    project_id: int,
    checks: dict,
    issues: list,
    scores: dict,
    overall_score: int,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    report = create_stability_report(db, project_id, checks, issues, scores, overall_score)
    return {
        "id": report.id,
        "overallScore": report.overall_score,
        "generatedAt": report.generated_at
    }


@router.post("/stability/check")
async def check_stability(script: str = Body(..., embed=True)):
    checker = StabilityChecker()
    result = checker.analyze(script)
    return result


@router.post("/stability/fix")
async def fix_stability(script: str = Body(..., embed=True)):
    checker = StabilityChecker()
    fixed_script, fixes = checker.auto_fix(script)
    return {
        "fixedScript": fixed_script,
        "fixes": fixes
    }


@router.post("/projects/{project_id}/stability/check-all")
async def check_project_stability(project_id: int, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    cases, _ = get_test_cases(db, project_id)
    all_issues = []
    all_scores = {}
    overall_score = 0
    case_results = []
    
    for case in cases:
        if case.script:
            checker = StabilityChecker()
            result = checker.analyze(case.script, case.title)
            case_results.append({
                "id": case.id,
                "title": case.title,
                "module": case.module or "",
                "overall_score": result["overall_score"],
                "scores": result["scores"],
                "checks": result["checks"],
                "issues": result["issues"],
            })
            all_issues.extend(result["issues"])
            for key, value in result["scores"].items():
                if key not in all_scores:
                    all_scores[key] = []
                all_scores[key].append(value)
    
    if all_scores:
        for key in all_scores:
            all_scores[key] = int(sum(all_scores[key]) / len(all_scores[key]))
        overall_score = int(sum(all_scores.values()) / len(all_scores))
    
    checks_summary = {
        "selector_stability": {
            "label": "选择器稳定性",
            "risk_count": sum(1 for r in case_results for i in r["issues"] if i["type"] == "selector_stability"),
            "fixed_count": sum(r["checks"].get("selector_stability", {}).get("fixed_count", 0) for r in case_results),
            "suggestion": "已自动优化" if any(r["checks"].get("selector_stability", {}).get("fixed_count", 0) > 0 for r in case_results) else "建议优化选择器",
            "tag": "success" if not case_results else ("success" if all(r["checks"].get("selector_stability", {}).get("passed", False) and r["checks"].get("selector_stability", {}).get("risk_count", 0) == r["checks"].get("selector_stability", {}).get("fixed_count", 0) for r in case_results) else "warning"),
        },
        "login_state": {
            "label": "登录态注入",
            "risk_count": sum(1 for r in case_results if r["checks"].get("login_state", {}).get("needs_login", False)),
            "fixed_count": sum(1 for r in case_results if r["checks"].get("login_state", {}).get("has_storage_state", False)),
            "suggestion": "已自动注入" if any(r["checks"].get("login_state", {}).get("has_storage_state", False) for r in case_results) else ("需配置登录态" if any(r["checks"].get("login_state", {}).get("needs_login", False) for r in case_results) else "无需登录"),
            "tag": "success" if all(not r["checks"].get("login_state", {}).get("needs_login", False) or r["checks"].get("login_state", {}).get("has_storage_state", False) for r in case_results) else "warning" if case_results else "info",
        },
        "wait_strategy": {
            "label": "等待机制",
            "risk_count": sum(r["checks"].get("wait_strategy", {}).get("bad_wait_count", 0) for r in case_results),
            "fixed_count": sum(r["checks"].get("wait_strategy", {}).get("web_first_count", 0) for r in case_results),
            "suggestion": "已替换为auto-wait" if any(r["checks"].get("wait_strategy", {}).get("bad_wait_count", 0) > 0 for r in case_results) else "建议使用Web-First断言",
            "tag": "success" if all(r["checks"].get("wait_strategy", {}).get("passed", False) for r in case_results) else "warning" if case_results else "info",
        },
        "dynamic_data": {
            "label": "动态数据",
            "risk_count": sum(1 for r in case_results if r["checks"].get("dynamic_data", {}).get("has_hardcoded", False)),
            "fixed_count": sum(1 for r in case_results if r["checks"].get("dynamic_data", {}).get("has_faker", False)),
            "suggestion": "已配置Faker" if any(r["checks"].get("dynamic_data", {}).get("has_faker", False) for r in case_results) else ("需配置动态数据" if any(r["checks"].get("dynamic_data", {}).get("has_hardcoded", False) for r in case_results) else "无需配置"),
            "tag": "success" if all(not r["checks"].get("dynamic_data", {}).get("has_hardcoded", False) or r["checks"].get("dynamic_data", {}).get("has_faker", False) for r in case_results) else "warning" if case_results else "info",
        },
    }
    
    create_stability_report(db, project_id, checks_summary, all_issues, all_scores, overall_score)
    
    return {
        "projectId": project_id,
        "caseCount": len(cases),
        "totalIssues": len(all_issues),
        "scores": all_scores,
        "overallScore": overall_score,
        "checks": checks_summary,
        "cases": case_results,
    }


# ==================== 评审报告 ====================

@router.get("/projects/{project_id}/review")
async def get_project_review(project_id: int, db: Session = Depends(get_db)):
    report = get_review_report(db, project_id)
    if not report:
        return {"score": 0, "metrics": [], "suggestions": [], "isExpired": False}
    return {
        "id": report.id,
        "projectId": report.project_id,
        "score": report.score,
        "metrics": report.metrics,
        "suggestions": report.suggestions,
        "reqSource": report.req_source,
        "model": report.model,
        "isExpired": bool(report.is_expired) if hasattr(report, "is_expired") else False,
        "reviewedAt": report.reviewed_at
    }


@router.post("/projects/{project_id}/review/generate")
async def generate_project_review(project_id: int, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 只取最新一次需求分析（按 id 降序），避免历史需求污染评审范围
    requirements = get_requirements(db, project_id)
    if not requirements:
        raise HTTPException(status_code=400, detail="项目没有需求分析结果，请先进行需求分析")

    latest_req = max(requirements, key=lambda r: r.id)
    if not (latest_req.analysis_result and latest_req.analysis_result.get("feature_points")):
        raise HTTPException(status_code=400, detail="最新需求没有需求分析结果，请先进行需求分析")

    feature_points = latest_req.analysis_result["feature_points"]
    req_source = latest_req.title or ""

    # 只评审与最新需求关联的用例；若没有关联用例则回退到项目全部用例
    cases = db.query(TestCase).filter(
        TestCase.project_id == project_id,
        TestCase.requirement_id == latest_req.id
    ).all()
    if not cases:
        cases, _ = get_test_cases(db, project_id)
    if not cases:
        raise HTTPException(status_code=400, detail="项目没有测试用例，请先生成用例")

    ai_cases = []
    case_id_list = []
    for case in cases:
        case_id_list.append(case.id)
        ai_cases.append(GeneratedCase(
            title=case.title,
            module=case.module or "",
            priority=case.priority or "P1",
            precondition=case.precondition or "",
            steps=case.steps or [],
            expected=case.expected or "",
            script=case.script or "",
            stability_score=80,
        ))

    ai_feature_points = []
    for fp in feature_points:
        ai_feature_points.append(FeaturePoint(
            name=fp.get("name", ""),
            priority=fp.get("priority", "P1"),
            test_dimensions=fp.get("test_dimensions", []),
            business_logic=fp.get("business_logic", ""),
            risk_hint=fp.get("risk_hint", ""),
        ))

    ai = AIService()
    result = await ai.review_cases(ai_cases, ai_feature_points, case_ids=case_id_list)

    metrics = [
        {"label": "需求覆盖度", "value": f"{result.coverage_score}%", "tag": "success" if result.coverage_score >= 80 else "warning" if result.coverage_score >= 60 else "danger"},
        {"label": "场景完整性", "value": f"{result.completeness_score}%", "tag": "success" if result.completeness_score >= 80 else "warning" if result.completeness_score >= 60 else "danger"},
        {"label": "可执行性", "value": f"{result.executability_score}%", "tag": "success" if result.executability_score >= 80 else "warning" if result.executability_score >= 60 else "danger"},
    ]

    suggestions = []
    for idx, s in enumerate(result.suggestions):
        tag = "warning"
        if idx == 0 and result.overall_score < 70:
            tag = "danger"
        elif result.overall_score >= 80:
            tag = "success"
        suggestions.append({
            "tag": tag,
            "label": f"建议#{idx + 1}",
            "title": s.case_title,
            "problem": s.problem or s.issue,
            "suggestion": s.suggestion,
            "code": s.example,
            "suggestionUid": None,  # 创建后回填
            "caseId": s.case_id,
            "fieldPath": s.field_path,
            "issueType": s.issue_type,
            "severity": s.severity,
        })

    report = create_review_report(db, project_id, result.overall_score, metrics, suggestions, req_source, "DeepSeek-V4")

    # 持久化结构化建议到 review_suggestions 表
    for idx, s in enumerate(result.suggestions):
        if s.case_id is None:
            continue
        suggestion_uid = f"S-{report.id}-{str(idx + 1).zfill(3)}"
        create_review_suggestion(
            db,
            suggestion_uid=suggestion_uid,
            review_report_id=report.id,
            project_id=project_id,
            case_id=s.case_id,
            field_path=s.field_path,
            issue_type=s.issue_type,
            severity=s.severity,
            problem=s.problem or s.issue,
            suggestion=s.suggestion,
            sample_patch=s.sample_patch,
        )
        suggestions[idx]["suggestionUid"] = suggestion_uid

        # 更新用例评审状态
        update_test_case_review_status(db, s.case_id, "needs_modification")

    return {
        "score": result.overall_score,
        "subtitle": '评审已完成，有优化建议' if suggestions else '评审已完成',
        "reqSource": req_source,
        "time": result.summary,
        "model": "DeepSeek-V4",
        "metrics": metrics,
        "suggestions": suggestions,
        "summary": result.summary,
    }


@router.post("/projects/{project_id}/review")
async def save_review_report(
    project_id: int,
    score: int,
    metrics: dict,
    suggestions: list,
    req_source: Optional[str] = None,
    model: Optional[str] = None,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    report = create_review_report(db, project_id, score, metrics, suggestions, req_source, model)
    return {
        "id": report.id,
        "score": report.score,
        "reviewedAt": report.reviewed_at
    }


# ==================== 评审建议定向修改 ====================

# issue_type 中文标签映射
_ISSUE_TYPE_LABELS = {
    "coverage_gap": "覆盖缺失",
    "boundary_missing": "边界缺失",
    "assertion_weak": "断言薄弱",
    "script_risk": "脚本风险",
    "duplicate_case": "用例重复",
}


@router.get("/reviews/{review_id}/suggestions")
async def list_review_suggestions(
    review_id: int,
    status: Optional[str] = None,
    caseId: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """获取评审报告下的建议列表"""
    report = get_review_report_by_id(db, review_id)
    if not report:
        raise HTTPException(status_code=404, detail="评审报告不存在")

    items = get_suggestions_by_review(db, review_id, status=status, case_id=caseId)

    suggestions = []
    for item in items:
        case = db.query(TestCase).filter(TestCase.id == item.case_id).first()
        suggestions.append({
            "id": item.suggestion_uid,
            "reviewId": item.review_report_id,
            "caseId": item.case_id,
            "caseTitle": case.title if case else "",
            "fieldPath": item.field_path,
            "issueType": item.issue_type,
            "issueTypeLabel": _ISSUE_TYPE_LABELS.get(item.issue_type, item.issue_type),
            "severity": item.severity,
            "problem": item.problem,
            "suggestion": item.suggestion,
            "samplePatch": item.sample_patch,
            "status": item.status,
            "handledBy": item.handled_by,
            "handledAt": item.handled_at,
            "createdAt": item.created_at,
        })

    return {
        "reviewId": review_id,
        "projectId": report.project_id,
        "score": report.score,
        "isExpired": bool(report.is_expired) if hasattr(report, "is_expired") else False,
        "suggestions": suggestions,
    }


@router.get("/review-suggestions/{suggestion_uid}")
async def get_suggestion_detail(suggestion_uid: str, db: Session = Depends(get_db)):
    """获取单条建议详情"""
    item = get_suggestion_by_uid(db, suggestion_uid)
    if not item:
        raise HTTPException(status_code=404, detail="建议不存在")

    case = db.query(TestCase).filter(TestCase.id == item.case_id).first()

    return {
        "id": item.suggestion_uid,
        "reviewId": item.review_report_id,
        "caseId": item.case_id,
        "caseTitle": case.title if case else "",
        "caseModule": case.module if case else "",
        "fieldPath": item.field_path,
        "issueType": item.issue_type,
        "issueTypeLabel": _ISSUE_TYPE_LABELS.get(item.issue_type, item.issue_type),
        "severity": item.severity,
        "problem": item.problem,
        "suggestion": item.suggestion,
        "samplePatch": item.sample_patch,
        "status": item.status,
        "handledBy": item.handled_by,
        "handledAt": item.handled_at,
        "ignoreReason": item.ignore_reason,
        "caseInfo": {
            "id": case.id,
            "title": case.title,
            "module": case.module,
            "priority": case.priority,
            "status": case.status,
            "reviewStatus": case.review_status if hasattr(case, "review_status") else None,
            "version": case.version if hasattr(case, "version") else 1,
        } if case else None,
    }


@router.patch("/review-suggestions/{suggestion_uid}/status")
async def update_suggestion_status_api(
    suggestion_uid: str,
    body: SuggestionStatusUpdate,
    db: Session = Depends(get_db),
):
    """更新建议状态（忽略/恢复）"""
    item = get_suggestion_by_uid(db, suggestion_uid)
    if not item:
        raise HTTPException(status_code=404, detail="建议不存在")

    # 状态流转校验
    current = item.status
    if current == "resolved":
        raise HTTPException(status_code=400, detail="已处理的建议不允许变更状态")
    if body.status == "ignored" and current not in ("pending", "editing"):
        raise HTTPException(status_code=400, detail="当前状态不允许忽略操作")
    if body.status == "pending" and current != "ignored":
        raise HTTPException(status_code=400, detail="仅已忽略的建议可以恢复处理")

    if body.status == "ignored" and not body.ignore_reason:
        raise HTTPException(status_code=400, detail="忽略建议时需填写忽略原因")

    updated = update_suggestion_status(
        db,
        suggestion_uid,
        body.status,
        handled_by="user",
        ignore_reason=body.ignore_reason,
    )

    return {
        "id": updated.suggestion_uid,
        "status": updated.status,
        "handledBy": updated.handled_by,
        "handledAt": updated.handled_at,
        "ignoreReason": updated.ignore_reason,
    }


@router.get("/cases/{case_id}")
async def get_case_for_edit(
    case_id: int,
    suggestionId: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """用例定向查询（含版本号、关联建议）"""
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="该用例已不存在，可能已被删除")

    # 查询关联建议
    suggestions = []
    if suggestionId:
        all_suggestions = get_suggestions_by_case(db, case_id)
        for s in all_suggestions:
            suggestions.append({
                "id": s.suggestion_uid,
                "fieldPath": s.field_path,
                "problem": s.problem,
                "suggestion": s.suggestion,
                "status": s.status,
                "severity": s.severity,
                "isCurrent": s.suggestion_uid == suggestionId,
            })
        # 当前建议置顶
        suggestions.sort(key=lambda x: 0 if x["isCurrent"] else 1)

    return {
        "id": case.id,
        "projectId": case.project_id,
        "title": case.title,
        "module": case.module,
        "priority": case.priority,
        "precondition": case.precondition,
        "steps": case.steps,
        "expected": case.expected,
        "script": case.script,
        "scriptPath": case.script_path if hasattr(case, "script_path") else None,
        "status": case.status,
        "reviewStatus": case.review_status if hasattr(case, "review_status") else None,
        "version": case.version if hasattr(case, "version") else 1,
        "loginMode": case.login_mode,
        "loginRole": case.login_role,
        "createdAt": case.created_at,
        "updatedAt": case.updated_at,
        "suggestions": suggestions,
        "canEdit": True,
        "lockedBy": None,
    }


@router.patch("/cases/{case_id}")
async def update_case_with_review(
    case_id: int,
    body: CaseUpdateRequest,
    db: Session = Depends(get_db),
):
    """保存用例修改（含乐观锁和建议状态回写）"""
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="该用例已不存在，可能已被删除")

    update_fields = {
        "title": body.title,
        "precondition": body.precondition,
        "steps": body.steps,
        "expected": body.expected,
        "script": body.script,
    }

    updated, error = update_case_with_suggestion(
        db,
        case_id,
        update_fields=update_fields,
        expected_version=body.version,
        suggestion_uid=body.suggestion_id,
        handled_by="user",
    )

    if error == "CASE_NOT_FOUND":
        raise HTTPException(status_code=404, detail="该用例已不存在")
    if error == "VERSION_CONFLICT":
        raise HTTPException(
            status_code=409,
            detail="用例版本冲突，请刷新后重试",
            headers={"X-Error-Code": "VERSION_CONFLICT",
                     "X-Server-Version": str(case.version)},
        )
    if error:
        raise HTTPException(status_code=500, detail=f"保存失败: {error}")

    return {
        "id": updated.id,
        "version": updated.version,
        "reviewStatus": updated.review_status,
        "suggestionStatus": "resolved" if body.suggestion_id else None,
        "message": "已保存，建议状态已更新" if body.suggestion_id else "已保存",
        "canRecheck": True,
    }


@router.post("/cases/{case_id}/review")
async def review_single_case(case_id: int, db: Session = Depends(get_db)):
    """重新评审单条用例"""
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="该用例已不存在")

    # 获取项目的功能点
    requirements = get_requirements(db, case.project_id)
    feature_points = []
    for req in requirements:
        if req.analysis_result and req.analysis_result.get("feature_points"):
            feature_points.extend(req.analysis_result["feature_points"])

    if not feature_points:
        raise HTTPException(status_code=400, detail="项目没有需求分析结果，无法评审")

    ai_case = GeneratedCase(
        title=case.title,
        module=case.module or "",
        priority=case.priority or "P1",
        precondition=case.precondition or "",
        steps=case.steps or [],
        expected=case.expected or "",
        script=case.script or "",
        stability_score=80,
    )

    ai_feature_points = []
    for fp in feature_points:
        ai_feature_points.append(FeaturePoint(
            name=fp.get("name", ""),
            priority=fp.get("priority", "P1"),
            test_dimensions=fp.get("test_dimensions", []),
            business_logic=fp.get("business_logic", ""),
            risk_hint=fp.get("risk_hint", ""),
        ))

    ai = AIService()
    try:
        result = await ai.review_single_case(ai_case, ai_feature_points, case_id=case_id)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=f"重新评审未启动: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新评审失败: {type(e).__name__}: {e}")

    # 评审通过（无新建议）
    if not result.suggestions:
        update_test_case_review_status(db, case_id, "review_passed")
        return {
            "taskId": f"review-{case_id}-{int(datetime.now(timezone.utc).timestamp())}",
            "caseId": case_id,
            "status": "completed",
            "reviewResult": {
                "passed": True,
                "score": result.overall_score,
                "newSuggestions": [],
            },
            "message": "复审通过，用例状态已更新为已通过",
        }

    # 评审仍有问题：创建新建议
    for idx, s in enumerate(result.suggestions):
        if s.case_id is None:
            continue
        suggestion_uid = f"S-recheck-{case_id}-{str(idx + 1).zfill(3)}"
        create_review_suggestion(
            db,
            suggestion_uid=suggestion_uid,
            review_report_id=0,  # 重新评审不绑定特定报告
            project_id=case.project_id,
            case_id=case_id,
            field_path=s.field_path,
            issue_type=s.issue_type,
            severity=s.severity,
            problem=s.problem or s.issue,
            suggestion=s.suggestion,
            sample_patch=s.sample_patch,
        )

    update_test_case_review_status(db, case_id, "needs_modification")

    new_suggestions = [
        {
            "id": f"S-recheck-{case_id}-{str(idx + 1).zfill(3)}",
            "fieldPath": s.field_path,
            "issueType": s.issue_type,
            "severity": s.severity,
            "problem": s.problem or s.issue,
            "suggestion": s.suggestion,
        }
        for idx, s in enumerate(result.suggestions)
        if s.case_id is not None
    ]

    return {
        "taskId": f"review-{case_id}-{int(datetime.now(timezone.utc).timestamp())}",
        "caseId": case_id,
        "status": "completed",
        "reviewResult": {
            "passed": False,
            "score": result.overall_score,
            "newSuggestions": new_suggestions,
        },
        "message": "复审仍有问题，已生成新的改进建议",
    }


# ==================== 执行管理 ====================

@router.get("/projects/{project_id}/executions")
async def list_executions(project_id: int, db: Session = Depends(get_db)):
    executions = get_executions(db, project_id=project_id)
    return [
        {
            "id": e.id,
            "projectId": e.project_id,
            "batchId": e.batch_id,
            "status": e.status,
            "total": e.total,
            "passed": e.passed,
            "failed": e.failed,
            "items": e.items,
            "startedAt": e.started_at,
            "finishedAt": e.finished_at
        }
        for e in executions
    ]


@router.post("/projects/{project_id}/executions")
async def create_execution_batch(
    project_id: int,
    body: ExecutionCreate,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    execution = create_execution(db, project_id, body.batch_id or '', body.total)
    return {
        "id": execution.id,
        "batchId": execution.batch_id,
        "status": execution.status,
        "startedAt": execution.started_at
    }


@router.get("/executions/{exec_id}")
async def get_execution_detail(exec_id: int, db: Session = Depends(get_db)):
    execution = get_execution(db, exec_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return {
        "id": execution.id,
        "projectId": execution.project_id,
        "batchId": execution.batch_id,
        "status": execution.status,
        "total": execution.total,
        "passed": execution.passed,
        "failed": execution.failed,
        "items": execution.items,
        "logs": execution.logs,
        "startedAt": execution.started_at,
        "finishedAt": execution.finished_at
    }


@router.put("/executions/{exec_id}")
async def update_execution_status(
    exec_id: int,
    body: ExecutionUpdate,
    db: Session = Depends(get_db)
):
    update_data = {}
    if body.status:
        update_data["status"] = body.status
    if body.passed is not None:
        update_data["passed"] = body.passed
    if body.failed is not None:
        update_data["failed"] = body.failed
    if body.items:
        update_data["items"] = body.items
    if body.finished_at:
        try:
            dt = datetime.fromisoformat(body.finished_at.replace('Z', '+00:00'))
            # 统一转换为 UTC naive datetime，与 started_at 存储格式一致
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            update_data["finished_at"] = dt
        except (ValueError, AttributeError):
            update_data["finished_at"] = datetime.utcnow()

    updated = update_execution(db, exec_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return {"id": updated.id, "status": updated.status}


@router.delete("/executions/{exec_id}")
async def remove_execution(exec_id: int, db: Session = Depends(get_db)):
    """删除执行记录及其关联的测试报告"""
    success = delete_execution(db, exec_id)
    if not success:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return {"success": True, "message": "执行记录及关联报告已删除"}


# ==================== 测试报告 ====================

@router.get("/projects/{project_id}/reports")
async def list_project_reports(project_id: int, db: Session = Depends(get_db)):
    """获取项目下所有历史报告（关联执行批次）"""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    executions = get_executions(db, project_id)
    result = []
    for exe in executions:
        report = get_test_report(db, exe.id)
        items = exe.items if isinstance(exe.items, list) else []
        total = exe.total or len(items)
        passed = exe.passed or 0
        failed = exe.failed or 0
        result.append({
            "executionId": exe.id,
            "batchId": exe.batch_id or f"BATCH-{exe.id}",
            "status": exe.status or "unknown",
            "total": total,
            "passed": passed,
            "failed": failed,
            "passRate": f"{(passed / total * 100):.1f}%" if total else "0%",
            "startedAt": exe.started_at.isoformat() + '+00:00' if exe.started_at else None,
            "finishedAt": exe.finished_at.isoformat() + '+00:00' if exe.finished_at else None,
            "hasReport": report is not None,
            "reportId": report.id if report else None,
            "items": items,
            "fails": report.fails if report and isinstance(report.fails, list) else [],
            "logs": exe.logs if isinstance(exe.logs, list) else [],
            "generatedAt": report.generated_at.isoformat() + '+00:00' if report and report.generated_at else None,
        })
    return result


@router.post("/executions/{exec_id}/logs")
async def add_execution_log_api(
    exec_id: int,
    body: dict,
    db: Session = Depends(get_db)
):
    level = body.get("level", "info")
    message = body.get("message", "")
    add_execution_log(db, exec_id, level, message)
    return {"status": "ok"}


@router.get("/executions/{exec_id}/report")
async def get_execution_report(exec_id: int, db: Session = Depends(get_db)):
    execution = get_execution(db, exec_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    report = get_test_report(db, exec_id)
    if not report:
        return {
            "id": None,
            "executionId": exec_id,
            "passRate": "0%",
            "trends": {},
            "modules": {},
            "fails": [],
            "generatedAt": None,
            "message": "该执行批次尚未生成报告"
        }
    return {
        "id": report.id,
        "executionId": report.execution_id,
        "passRate": report.pass_rate,
        "trends": report.trends,
        "modules": report.modules,
        "fails": report.fails,
        "generatedAt": report.generated_at
    }


@router.post("/executions/{exec_id}/report")
async def save_test_report(
    exec_id: int,
    body: TestReportCreate,
    db: Session = Depends(get_db)
):
    execution = get_execution(db, exec_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")

    report = create_test_report(db, exec_id, body.pass_rate, body.trends, body.modules, body.fails)
    return {
        "id": report.id,
        "passRate": report.pass_rate,
        "generatedAt": report.generated_at
    }


# ==================== 系统设置 ====================

@router.get("/settings")
async def list_settings(db: Session = Depends(get_db)):
    settings = get_all_settings(db)
    return [
        {
            "id": s.id,
            "category": s.category,
            "key": s.key,
            "value": s.value,
            "description": s.description,
            "updatedAt": s.updated_at
        }
        for s in settings
    ]


@router.get("/settings/{category}")
async def list_settings_by_category(category: str, db: Session = Depends(get_db)):
    settings = get_settings_by_category(db, category)
    return [
        {
            "id": s.id,
            "category": s.category,
            "key": s.key,
            "value": s.value,
            "description": s.description,
            "updatedAt": s.updated_at
        }
        for s in settings
    ]


@router.get("/settings/{category}/{key}")
async def get_setting_value(category: str, key: str, db: Session = Depends(get_db)):
    setting = get_setting(db, category, key)
    if not setting:
        raise HTTPException(status_code=404, detail="设置不存在")
    return {
        "category": setting.category,
        "key": setting.key,
        "value": setting.value,
        "description": setting.description
    }


@router.post("/settings/{category}/{key}")
async def save_setting(
    category: str,
    key: str,
    body: SettingSaveRequest,
    db: Session = Depends(get_db)
):
    setting = set_setting(db, category, key, body.value, body.description)
    return {
        "category": setting.category,
        "key": setting.key,
        "value": setting.value,
        "description": setting.description,
        "updatedAt": setting.updated_at
    }


# ==================== Dashboard 统计 ====================

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    projects = get_projects(db)
    project_count = len(projects)
    
    total_cases = 0
    total_executions = 0
    total_passed = 0
    total_failed = 0

    for project in projects:
        _, cases_count = get_test_cases(db, project.id, page=1, page_size=1)
        total_cases += cases_count
        executions = get_executions(db, project.id)
        total_executions += len(executions)
        for exec in executions:
            total_passed += exec.passed or 0
            total_failed += exec.failed or 0

    total_run = total_passed + total_failed
    return {
        "projectCount": project_count,
        "totalCases": total_cases,
        "totalExecutions": total_executions,
        "totalPassed": total_passed,
        "totalFailed": total_failed,
        "passRate": f"{(total_passed / total_run * 100):.1f}%" if total_run > 0 else "0%"
    }


# ==================== 登录态配置 ====================

LOGIN_PROFILE_LIMIT = 5  # 每个项目最多5个登录态配置


def _profile_to_dict(p):
    """将 LoginProfile 转为前端字典"""
    valid_until_str = p.valid_until.isoformat() + '+00:00' if p.valid_until else None
    return {
        "id": p.id,
        "projectId": p.project_id,
        "name": p.name,
        "role": p.role,
        "username": p.username,
        "password": p.password,
        "storageStatePath": p.storage_state_path,
        "validDays": p.valid_days,
        "validUntil": valid_until_str,
        "status": p.status,
        "isDefault": bool(p.is_default),
        "createdAt": p.created_at.isoformat() + '+00:00' if p.created_at else None,
        "updatedAt": p.updated_at.isoformat() + '+00:00' if p.updated_at else None,
        # 登录脚本配置
        "loginUrl": p.login_url,
        "usernameSelector": p.username_selector,
        "usernameSelectorType": p.username_selector_type,
        "passwordSelector": p.password_selector,
        "passwordSelectorType": p.password_selector_type,
        "submitSelector": p.submit_selector,
        "submitSelectorType": p.submit_selector_type,
        "successIndicator": p.success_indicator,
        "successIndicatorType": p.success_indicator_type,
        "scriptMode": p.script_mode,
        "customScript": p.custom_script,
    }


@router.get("/projects/{project_id}/login-profiles")
async def list_login_profiles(project_id: int, db: Session = Depends(get_db)):
    """获取项目的所有登录态配置（含匿名）"""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    profiles = get_login_profiles(db, project_id)
    result = [_profile_to_dict(p) for p in profiles]
    # 匿名为系统内置，始终放在最前
    anonymous = {
        "id": "anonymous",
        "projectId": project_id,
        "name": "匿名(无登录态)",
        "role": "guest",
        "username": None,
        "password": None,
        "storageStatePath": None,
        "validDays": 0,
        "validUntil": None,
        "status": "always-valid",
        "isDefault": len(profiles) == 0,  # 无任何配置时匿名作为默认
        "createdAt": None,
        "updatedAt": None,
        "loginUrl": None,
        "usernameSelector": None, "usernameSelectorType": None,
        "passwordSelector": None, "passwordSelectorType": None,
        "submitSelector": None, "submitSelectorType": None,
        "successIndicator": None, "successIndicatorType": None,
        "scriptMode": "form", "customScript": None,
    }
    return [anonymous] + result


@router.post("/projects/{project_id}/login-profiles")
async def add_login_profile(
    project_id: int,
    req: LoginProfileCreate,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    # 校验上限（不含匿名，实际可配置4个 + 匿名1个 = 5个）
    current_count = count_login_profiles(db, project_id)
    if current_count >= LOGIN_PROFILE_LIMIT - 1:
        raise HTTPException(
            status_code=400,
            detail=f"已达上限{LOGIN_PROFILE_LIMIT - 1}个可配置登录态（外加1个匿名），请先删除不需要的"
        )
    profile = create_login_profile(
        db, project_id, req.name, req.role, req.username, req.password,
        req.storageStatePath, req.validDays, req.isDefault,
        login_url=req.loginUrl,
        username_selector=req.usernameSelector, username_selector_type=req.usernameSelectorType,
        password_selector=req.passwordSelector, password_selector_type=req.passwordSelectorType,
        submit_selector=req.submitSelector, submit_selector_type=req.submitSelectorType,
        success_indicator=req.successIndicator, success_indicator_type=req.successIndicatorType,
        script_mode=req.scriptMode, custom_script=req.customScript
    )
    return _profile_to_dict(profile)


@router.put("/login-profiles/{profile_id}")
async def update_login_profile_api(
    profile_id: int,
    req: LoginProfileUpdate,
    db: Session = Depends(get_db)
):
    profile = get_login_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="登录态配置不存在")
    update_data = req.model_dump(exclude_none=True)
    updated = update_login_profile(db, profile_id, **update_data)
    return _profile_to_dict(updated)


@router.post("/login-profiles/{profile_id}/generate-session")
async def generate_login_session(profile_id: int, db: Session = Depends(get_db)):
    """自动生成登录会话：执行 Playwright 登录脚本，保存 storageState 文件"""
    profile = get_login_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="登录态配置不存在")

    # 获取项目的应用 URL 作为 login_url 的默认值
    project = get_project(db, profile.project_id)
    app_url = project.app_url if project else None

    # 执行登录脚本
    generator = LoginSessionGenerator()
    result = await generator.generate_session(profile, profile.project_id, app_url)

    if result["success"]:
        # 成功：更新 profile 的 storageStatePath、validUntil、status
        update_login_profile(
            db, profile_id,
            storageStatePath=result["storageStatePath"],
            status="valid",
        )
        # update_login_profile 会自动计算 validUntil（因为填了 storageStatePath）
        db.refresh(profile)
        updated = get_login_profile(db, profile_id)
        return {
            "success": True,
            "message": "登录会话已生成",
            "profile": _profile_to_dict(updated),
            "duration_ms": result["duration_ms"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "screenshots": result["screenshots"],
        }
    else:
        error_info = result.get("error")
        error_message = error_info["message"] if isinstance(error_info, dict) else (error_info or "登录会话生成失败")
        return {
            "success": False,
            "message": error_message,
            "duration_ms": result.get("duration_ms", 0),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "screenshots": result.get("screenshots", []),
            "error": error_info,
        }


@router.delete("/login-profiles/{profile_id}")
async def remove_login_profile(profile_id: int, db: Session = Depends(get_db)):
    success = delete_login_profile(db, profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="登录态配置不存在")
    return {"success": True, "message": "登录态配置已删除"}


@router.get("/projects/{project_id}/login-profiles/default")
async def get_default_profile(project_id: int, db: Session = Depends(get_db)):
    """获取项目的默认登录态"""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    profile = get_default_login_profile(db, project_id)
    if not profile:
        # 返回匿名
        return {
            "id": "anonymous",
            "projectId": project_id,
            "name": "匿名(无登录态)",
            "role": "guest",
            "status": "always-valid",
            "isDefault": True,
        }
    return _profile_to_dict(profile)