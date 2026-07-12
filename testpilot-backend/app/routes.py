"""API 路由：3 个核心接口 + 健康检查 + 项目管理"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from .config import get_settings
from .models import (
    AnalyzeRequest,
    AnalyzeResponse,
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
    RequirementCreate,
    AnalysisSaveRequest,
    TestCaseCreate,
    TestCaseStatusUpdate,
    ExecutionRecordCreate,
    ExecutionCreate,
    ExecutionUpdate,
    TestReportCreate,
    SettingSaveRequest,
)
from .services import AIService, ExecutionService
from .stability_checker import StabilityChecker
from .database import get_db
from .crud import (
    get_projects,
    get_project,
    get_project_by_name,
    create_project,
    update_project,
    delete_project,
    create_requirement,
    get_requirements,
    get_requirement,
    update_requirement_analysis,
    create_test_case,
    get_test_cases,
    update_test_case_status,
    delete_test_case,
    create_execution_record,
    get_execution_records,
    create_stability_report,
    get_stability_report,
    create_review_report,
    get_review_report,
    create_execution,
    update_execution,
    get_execution,
    get_executions,
    create_test_report,
    get_test_report,
    get_setting,
    set_setting,
    get_settings_by_category,
    get_all_settings,
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
    
    ai = AIService()
    try:
        logger.debug(f"Analyzing requirement (stream): {req.requirement_text[:100]}...")
        
        prompt = req.requirement_text
        if req.app_url:
            prompt += f"\n\n被测应用 URL: {req.app_url}"
        
        prompt = ANALYZE_PROMPT.format(
            requirement_text=req.requirement_text,
            app_url=req.app_url or "未提供",
        )
        
        async def generate():
            buffer = ""
            async for chunk in ai.chat_stream(prompt):
                buffer += chunk
                yield f"data: {json.dumps({'type': 'progress', 'content': chunk, 'buffer_length': len(buffer)})}\n\n"
            
            try:
                text = buffer.strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                
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
            except json.JSONDecodeError as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'JSON 解析失败: {str(e)}', 'raw': buffer[:500]})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in analyze stream: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"需求分析失败: {type(e).__name__}: {e}")


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest) -> GenerateResponse:
    ai = AIService()
    try:
        return await ai.generate_scripts(req.feature_points, req.app_url)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脚本生成失败: {e}")


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
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "appUrl": p.app_url,
            "dim": p.dim,
            "techStack": p.tech_stack,
            "createdAt": p.created_at,
            "updatedAt": p.updated_at
        }
        for p in projects
    ]


@router.post("/projects")
async def add_project(
    req: ProjectCreate,
    db: Session = Depends(get_db)
):
    existing = get_project_by_name(db, req.name)
    if existing:
        raise HTTPException(status_code=400, detail="项目名称已存在")
    
    project = create_project(db, req.name, req.description, req.appUrl, req.dim, req.techStack)
    if not project:
        raise HTTPException(status_code=400, detail="创建项目失败")
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "appUrl": project.app_url,
        "dim": project.dim,
        "techStack": project.tech_stack,
        "createdAt": project.created_at
    }


@router.get("/projects/{project_id}")
async def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "appUrl": project.app_url,
        "dim": project.dim,
        "techStack": project.tech_stack,
        "createdAt": project.created_at,
        "updatedAt": project.updated_at
    }


@router.put("/projects/{project_id}")
async def update_project_detail(
    project_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    appUrl: Optional[str] = None,
    dim: Optional[str] = None,
    techStack: Optional[str] = None,
    db: Session = Depends(get_db)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    update_data = {}
    if name:
        update_data["name"] = name
    if description:
        update_data["description"] = description
    if appUrl:
        update_data["app_url"] = appUrl
    if dim:
        update_data["dim"] = dim
    if techStack:
        update_data["tech_stack"] = techStack
    
    updated = update_project(db, project_id, **update_data)
    return {
        "id": updated.id,
        "name": updated.name,
        "description": updated.description,
        "appUrl": updated.app_url,
        "dim": updated.dim,
        "techStack": updated.tech_stack,
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
                "stabilityScore": getattr(c, 'stability_score', 0) or 0
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
        body.steps, body.expected, body.script, body.scriptPath, body.requirementId
    )
    return {
        "id": case.id,
        "title": case.title,
        "status": case.status,
        "createdAt": case.created_at
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
async def check_stability(script: str):
    checker = StabilityChecker()
    result = checker.analyze(script)
    return result


@router.post("/stability/fix")
async def fix_stability(script: str):
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
            "tag": "success" if all(r["checks"].get("selector_stability", {}).get("passed", False) for r in case_results) else "warning" if case_results else "info",
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
        return {"score": 0, "metrics": [], "suggestions": []}
    return {
        "id": report.id,
        "projectId": report.project_id,
        "score": report.score,
        "metrics": report.metrics,
        "suggestions": report.suggestions,
        "reqSource": report.req_source,
        "model": report.model,
        "reviewedAt": report.reviewed_at
    }


@router.post("/projects/{project_id}/review/generate")
async def generate_project_review(project_id: int, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    cases, _ = get_test_cases(db, project_id)
    if not cases:
        raise HTTPException(status_code=400, detail="项目没有测试用例，请先生成用例")

    requirements = get_requirements(db, project_id)
    feature_points = []
    req_source = ""
    for req in requirements:
        if req.analysis_result and req.analysis_result.get("feature_points"):
            feature_points.extend(req.analysis_result["feature_points"])
            req_source = req.title or req_source

    if not feature_points:
        raise HTTPException(status_code=400, detail="项目没有需求分析结果，请先进行需求分析")

    ai_cases = []
    for case in cases:
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
    result = await ai.review_cases(ai_cases, ai_feature_points)

    metrics = [
        {"label": "需求覆盖度", "value": f"{result.coverage_score}%", "tag": "success" if result.coverage_score >= 80 else "warning" if result.coverage_score >= 60 else "danger"},
        {"label": "场景完整性", "value": f"{result.completeness_score}%", "tag": "success" if result.completeness_score >= 80 else "warning" if result.completeness_score >= 60 else "danger"},
        {"label": "可执行性", "value": f"{result.executability_score}%", "tag": "success" if result.executability_score >= 80 else "warning" if result.executability_score >= 60 else "danger"},
    ]

    suggestions = []
    tag_map = {"danger": 0, "warning": 1, "success": 2}
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
            "problem": s.issue,
            "suggestion": s.suggestion,
            "code": s.example,
        })

    create_review_report(db, project_id, result.overall_score, metrics, suggestions, req_source, "DeepSeek-V4")

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
            update_data["finished_at"] = datetime.fromisoformat(body.finished_at.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            update_data["finished_at"] = datetime.now()

    updated = update_execution(db, exec_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return {"id": updated.id, "status": updated.status}


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
            "startedAt": exe.started_at.isoformat() if exe.started_at else None,
            "finishedAt": exe.finished_at.isoformat() if exe.finished_at else None,
            "hasReport": report is not None,
            "reportId": report.id if report else None,
            "items": items,
            "fails": report.fails if report and isinstance(report.fails, list) else [],
            "generatedAt": report.generated_at.isoformat() if report and report.generated_at else None,
        })
    return result


@router.get("/executions/{exec_id}/report")
async def get_execution_report(exec_id: int, db: Session = Depends(get_db)):
    report = get_test_report(db, exec_id)
    if not report:
        return {"passRate": "0%", "trends": {}, "modules": {}, "fails": []}
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
    
    for project in projects:
        cases = get_test_cases(db, project.id)
        total_cases += len(cases)
        executions = get_executions(db, project.id)
        total_executions += len(executions)
        for exec in executions:
            total_passed += exec.passed or 0
    
    return {
        "projectCount": project_count,
        "totalCases": total_cases,
        "totalExecutions": total_executions,
        "totalPassed": total_passed,
        "passRate": f"{(total_passed / total_executions * 100):.1f}%" if total_executions > 0 else "0%"
    }