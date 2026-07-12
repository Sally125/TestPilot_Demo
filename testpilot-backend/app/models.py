"""Pydantic 数据模型：定义所有 API 的请求/响应结构"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ==================== 需求分析 ====================

class AnalyzeRequest(BaseModel):
    """需求分析请求"""
    requirement_text: str = Field(
        ..., min_length=10, description="需求文本，至少10个字符"
    )
    app_url: str | None = Field(default=None, description="被测应用 URL（可选）")


class FeaturePoint(BaseModel):
    """功能点"""
    name: str = Field(..., description="功能名称")
    priority: Literal["P0", "P1", "P2"] = Field(..., description="优先级")
    test_dimensions: list[str] = Field(
        default_factory=list, description="测试维度建议，如功能测试/边界值测试/异常输入测试"
    )
    business_logic: str = Field(default="", description="关键业务规则")
    risk_hint: str = Field(default="", description="风险提示")


class AnalyzeResponse(BaseModel):
    """需求分析响应"""
    feature_points: list[FeaturePoint] = Field(..., description="提取的功能点列表")
    summary: str = Field(default="", description="分析摘要")
    estimated_case_count: int = Field(default=0, description="预估用例数")
    raw: str | None = Field(default=None, description="AI 原始返回（调试用）")


# ==================== 脚本生成 ====================

class GenerateRequest(BaseModel):
    """脚本生成请求"""
    feature_points: list[FeaturePoint] = Field(..., min_length=1, description="功能点列表")
    app_url: str = Field(default="", description="被测应用 URL")
    case_title: str | None = Field(default=None, description="指定用例标题（可选）")


class GeneratedCase(BaseModel):
    """生成的测试用例"""
    title: str = Field(..., description="用例标题")
    module: str = Field(default="", description="所属功能模块")
    priority: Literal["P0", "P1", "P2"] = Field(default="P1", description="优先级")
    precondition: str = Field(default="", description="前置条件")
    steps: list[str] = Field(default_factory=list, description="操作步骤")
    expected: str = Field(default="", description="预期结果")
    script: str = Field(..., description="Playwright 脚本内容（完整可运行）")
    stability_score: int = Field(default=80, description="稳定性评分 0-100")


class GenerateResponse(BaseModel):
    """脚本生成响应"""
    cases: list[GeneratedCase] = Field(..., description="生成的测试用例列表")
    raw: str | None = Field(default=None, description="AI 原始返回（调试用）")


# ==================== 脚本执行 ====================

class RunRequest(BaseModel):
    """脚本执行请求"""
    script: str = Field(..., description="Playwright 脚本内容")
    app_url: str | None = Field(default=None, description="被测应用 URL（覆盖配置）")
    timeout: int | None = Field(default=None, description="超时时间（毫秒）")
    storage_state_path: str | None = Field(default=None, description="storageState 文件路径（覆盖配置）")


class RunResponse(BaseModel):
    """脚本执行响应"""
    passed: bool = Field(..., description="是否通过")
    duration_ms: int = Field(..., description="执行耗时（毫秒）")
    stdout: str = Field(default="", description="标准输出")
    stderr: str = Field(default="", description="错误输出")
    screenshots: list[str] = Field(default_factory=list, description="截图路径列表")
    error: str | None = Field(default=None, description="失败原因（若有）")


# ==================== 项目管理 ====================

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    appUrl: str | None = None
    dim: str | None = None
    techStack: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    appUrl: str | None = None
    dim: str | None = None
    techStack: str | None = None


# ==================== 通用 ====================

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    has_api_key: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


# ==================== 持久化请求模型 ====================

class RequirementCreate(BaseModel):
    """创建需求"""
    title: str
    content: str


class AnalysisSaveRequest(BaseModel):
    """保存分析结果"""
    analysis_result: dict


class TestCaseCreate(BaseModel):
    """创建测试用例"""
    title: str
    module: str | None = None
    priority: str = "P1"
    precondition: str | None = None
    steps: list | None = None
    expected: str | None = None
    script: str | None = None
    scriptPath: str | None = None
    requirementId: int | None = None


class TestCaseStatusUpdate(BaseModel):
    """更新用例状态"""
    status: str


class ExecutionRecordCreate(BaseModel):
    """创建执行记录"""
    project_id: int
    case_id: int
    passed: bool
    duration_ms: int | None = None
    error: str | None = None
    screenshots: list | None = None


class ExecutionCreate(BaseModel):
    """创建执行批次"""
    batch_id: str | None = None
    total: int = 0


class ExecutionUpdate(BaseModel):
    """更新执行批次"""
    status: str | None = None
    passed: int | None = None
    failed: int | None = None
    finished_at: str | None = None
    items: list | None = None


class TestReportCreate(BaseModel):
    """保存测试报告"""
    pass_rate: str
    trends: dict | None = None
    modules: dict | None = None
    fails: list | None = None


class SettingSaveRequest(BaseModel):
    """保存系统设置"""
    value: dict | list | str | int | None = None
    description: str | None = None


# ==================== 评审报告 ====================

class ReviewSuggestion(BaseModel):
    """改进建议"""
    case_title: str = Field(..., description="问题所在用例标题")
    issue: str = Field(..., description="问题描述")
    suggestion: str = Field(..., description="改进建议")
    example: str = Field(default="", description="代码示例（可选）")


class ReviewRequest(BaseModel):
    """评审请求"""
    cases: list[GeneratedCase] = Field(..., description="测试用例列表")
    feature_points: list[FeaturePoint] = Field(..., description="原始功能点列表")


class ReviewResponse(BaseModel):
    """评审报告响应"""
    overall_score: int = Field(..., description="综合质量评分 0-100")
    coverage_score: int = Field(..., description="需求覆盖度评分 0-100")
    completeness_score: int = Field(..., description="场景完整性评分 0-100")
    executability_score: int = Field(..., description="可执行性评分 0-100")
    suggestions: list[ReviewSuggestion] = Field(..., description="改进建议列表（3条）")
    summary: str = Field(..., description="整体评审摘要")
    raw: str | None = Field(default=None, description="AI 原始返回（调试用）")
