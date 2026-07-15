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

class DesignTestCasesRequest(BaseModel):
    """测试用例设计请求"""
    feature_points: list[FeaturePoint] = Field(..., min_length=1, description="功能点列表")


class TestCaseStep(BaseModel):
    """测试步骤"""
    step: int = Field(..., description="步骤序号")
    action: str = Field(..., description="操作动作")
    expected_result: str = Field(default="", description="步骤预期结果")
    page_element: str = Field(default="", description="操作的页面元素描述")


class TestCaseData(BaseModel):
    """测试数据"""
    description: str = Field(default="", description="测试数据描述")
    input_values: list[dict] = Field(default_factory=list, description="输入值列表")


class DesignedTestCase(BaseModel):
    """设计的测试用例"""
    id: str = Field(..., description="用例ID，如 TC-001")
    title: str = Field(..., description="用例标题")
    source_feature_id: str = Field(default="", description="来源功能点ID")
    source_feature_name: str = Field(default="", description="来源功能点名称")
    priority: Literal["P0", "P1", "P2"] = Field(default="P1", description="优先级")
    type: str = Field(default="功能测试", description="测试类型")
    module: str = Field(default="", description="所属功能模块")
    preconditions: str = Field(default="", description="前置条件")
    test_data: TestCaseData = Field(default_factory=TestCaseData, description="测试数据")
    steps: list[TestCaseStep] = Field(default_factory=list, description="操作步骤")
    expected_result: str = Field(default="", description="预期结果")
    verification_method: str = Field(default="", description="验证方法")
    tags: list[str] = Field(default_factory=list, description="标签")
    notes: str = Field(default="", description="备注")


class TestCaseSummary(BaseModel):
    """测试用例汇总"""
    requirement_title: str = Field(default="", description="需求标题")
    total_feature_points: int = Field(default=0, description="功能点总数")
    total_test_cases: int = Field(default=0, description="用例总数")
    p0_cases: int = Field(default=0, description="P0用例数")
    p1_cases: int = Field(default=0, description="P1用例数")
    p2_cases: int = Field(default=0, description="P2用例数")
    generation_time: str = Field(default="", description="生成时间")


class CoverageMatrixItem(BaseModel):
    """覆盖矩阵项"""
    feature_id: str = Field(..., description="功能点ID")
    feature_name: str = Field(..., description="功能点名称")
    covering_cases: list[str] = Field(default_factory=list, description="覆盖用例ID列表")
    covered_dimensions: list[str] = Field(default_factory=list, description="覆盖维度列表")


class CoverageMatrix(BaseModel):
    """覆盖矩阵"""
    description: str = Field(default="", description="描述")
    matrix: list[CoverageMatrixItem] = Field(default_factory=list, description="矩阵项")


class DesignTestCasesResponse(BaseModel):
    """测试用例设计响应"""
    testcase_summary: TestCaseSummary = Field(..., description="用例汇总")
    test_cases: list[DesignedTestCase] = Field(..., description="设计的测试用例列表")
    coverage_matrix: CoverageMatrix = Field(..., description="功能点覆盖矩阵")
    raw: str | None = Field(default=None, description="AI 原始返回（调试用）")


class GenerateRequest(BaseModel):
    """脚本生成请求"""
    test_cases: list[DesignedTestCase] = Field(..., min_length=1, description="测试用例列表")
    app_url: str = Field(default="", description="被测应用 URL")


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
    stability_checks: dict | None = Field(default=None, description="稳定性检测结果")
    stability_issues: list[dict] = Field(default_factory=list, description="稳定性问题列表")


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
    name: str = Field(..., min_length=1, max_length=100, description="项目名称（不能为空）")
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
    title: str = Field(..., min_length=1, description="需求标题（不能为空）")
    content: str = Field(..., min_length=1, description="需求内容（不能为空）")


class AnalysisSaveRequest(BaseModel):
    """保存分析结果"""
    analysis_result: dict


class TestCaseCreate(BaseModel):
    """创建测试用例"""
    title: str = Field(..., min_length=1, description="用例标题（不能为空）")
    module: str = Field(..., min_length=1, description="所属功能模块（不能为空）")
    priority: str = Field(default="P1", description="优先级 P0/P1/P2")
    precondition: str | None = None
    steps: list = Field(..., min_length=1, description="操作步骤（至少1步）")
    expected: str = Field(..., min_length=1, description="预期结果（不能为空）")
    script: str | None = None
    scriptPath: str | None = None
    requirementId: int | None = None
    loginMode: str = Field(default="global", description="登录态模式：global/specified/anonymous")
    loginRole: str | None = Field(default=None, description="指定登录态角色（仅 loginMode=specified 时使用）")


class LoginProfileCreate(BaseModel):
    """创建登录态配置"""
    name: str = Field(..., min_length=1, max_length=100, description="名称（不能为空）")
    role: str = Field(..., min_length=1, max_length=100, description="角色标识（不能为空）")
    username: str | None = Field(default=None, description="账号")
    password: str | None = Field(default=None, description="密码")
    storageStatePath: str | None = Field(default=None, description="storageState 文件路径")
    validDays: int = Field(default=7, ge=1, description="有效天数")
    isDefault: bool = Field(default=False, description="是否设为默认")
    # 登录脚本配置（用于自动生成 storageState）
    loginUrl: str | None = Field(default=None, description="登录页URL")
    usernameSelector: str | None = Field(default=None, description="用户名输入框选择器")
    usernameSelectorType: str | None = Field(default=None, description="用户名选择器类型：css/locator/placeholder")
    passwordSelector: str | None = Field(default=None, description="密码输入框选择器")
    passwordSelectorType: str | None = Field(default=None, description="密码选择器类型：css/locator/placeholder")
    submitSelector: str | None = Field(default=None, description="提交按钮选择器")
    submitSelectorType: str | None = Field(default=None, description="提交按钮选择器类型：css/locator/placeholder")
    successIndicator: str | None = Field(default=None, description="登录成功标志（URL或元素）")
    successIndicatorType: str | None = Field(default=None, description="成功标志类型：css/locator/placeholder/url")
    scriptMode: str = Field(default="form", description="脚本模式：form(表单)/custom(自定义脚本)")
    customScript: str | None = Field(default=None, description="自定义Playwright登录脚本代码")


class LoginProfileUpdate(BaseModel):
    """更新登录态配置"""
    name: str | None = None
    role: str | None = None
    username: str | None = None
    password: str | None = None
    storageStatePath: str | None = None
    validDays: int | None = Field(default=None, ge=1)
    status: str | None = None
    isDefault: bool | None = None
    # 登录脚本配置
    loginUrl: str | None = None
    usernameSelector: str | None = None
    usernameSelectorType: str | None = None
    passwordSelector: str | None = None
    passwordSelectorType: str | None = None
    submitSelector: str | None = None
    submitSelectorType: str | None = None
    successIndicator: str | None = None
    successIndicatorType: str | None = None
    scriptMode: str | None = None
    customScript: str | None = None


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
    case_index: int = Field(default=0, description="对应用例在输入列表中的索引")
    case_id: int | None = Field(default=None, description="关联用例 ID（后端映射）")
    field_path: list[str] = Field(default_factory=list, description="建议影响字段")
    issue_type: str = Field(default="coverage_gap", description="问题类型")
    severity: str = Field(default="medium", description="严重程度: high/medium/low")
    problem: str = Field(default="", description="问题描述")
    issue: str = Field(..., description="问题描述（兼容旧字段）")
    suggestion: str = Field(..., description="改进建议")
    sample_patch: dict | None = Field(default=None, description="AI 参考修改示例")
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


# ==================== 评审建议定向修改 ====================

class SuggestionStatusUpdate(BaseModel):
    """更新建议状态请求"""
    status: Literal["ignored", "pending"] = Field(
        ..., description="目标状态: ignored(忽略) / pending(恢复处理)"
    )
    ignore_reason: str | None = Field(
        default=None, max_length=500, description="忽略原因（仅 status=ignored 时填写）"
    )


class CaseUpdateRequest(BaseModel):
    """保存用例修改请求（含乐观锁和建议联动）"""
    title: str | None = Field(default=None, min_length=1, description="用例标题")
    precondition: str | None = None
    steps: list[str] | None = Field(default=None, min_length=1, description="操作步骤")
    expected: str | None = Field(default=None, min_length=1, description="预期结果")
    script: str | None = None
    version: int = Field(..., description="客户端持有的版本号（乐观锁）")
    suggestion_id: str | None = Field(default=None, description="关联建议 UID")
