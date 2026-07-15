from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    app_url = Column(String(500), nullable=True)
    dim = Column(String(100), nullable=True)
    tech_stack = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    analysis_result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    requirement_id = Column(Integer, nullable=True)
    title = Column(String(200), nullable=False)
    module = Column(String(100), nullable=True)
    priority = Column(String(10), nullable=False)
    precondition = Column(Text, nullable=True)
    steps = Column(JSON, nullable=True)
    expected = Column(Text, nullable=True)
    script = Column(Text, nullable=True)
    script_path = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    stability_score = Column(Integer, nullable=True)
    # 登录态绑定：global=跟随全局，specified=指定角色，anonymous=匿名
    login_mode = Column(String(20), nullable=False, default="global")
    login_role = Column(String(100), nullable=True)
    # 评审状态：NULL=未评审, needs_modification=需修改, modified_pending_review=已修改待复审, review_passed=已通过
    review_status = Column(String(30), nullable=True)
    # 乐观锁版本号，每次保存自增 1
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LoginProfile(Base):
    """登录态配置：每个项目最多5个（含匿名）"""
    __tablename__ = "login_profiles"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    username = Column(String(200), nullable=True)
    password = Column(String(500), nullable=True)
    storage_state_path = Column(String(500), nullable=True)
    valid_days = Column(Integer, nullable=False, default=7)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="ungenerated")
    is_default = Column(Integer, nullable=False, default=0)
    # 登录脚本配置（用于自动生成 storageState）
    login_url = Column(String(500), nullable=True)
    username_selector = Column(String(300), nullable=True)
    username_selector_type = Column(String(20), nullable=True)  # css/locator/placeholder
    password_selector = Column(String(300), nullable=True)
    password_selector_type = Column(String(20), nullable=True)
    submit_selector = Column(String(300), nullable=True)
    submit_selector_type = Column(String(20), nullable=True)
    success_indicator = Column(String(500), nullable=True)  # 登录成功的判断标志
    success_indicator_type = Column(String(20), nullable=True)  # css/locator/placeholder/url
    # 自定义脚本模式：用户直接写 Playwright 登录代码
    script_mode = Column(String(20), nullable=False, default="form")  # form/custom
    custom_script = Column(Text, nullable=True)  # 用户自定义的 Playwright 登录脚本代码
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ExecutionRecord(Base):
    __tablename__ = "execution_records"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    case_id = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    screenshots = Column(JSON, nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())


class StabilityReport(Base):
    __tablename__ = "stability_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    checks = Column(JSON, nullable=True)
    issues = Column(JSON, nullable=True)
    scores = Column(JSON, nullable=True)
    overall_score = Column(Integer, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class ReviewReport(Base):
    __tablename__ = "review_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    score = Column(Integer, nullable=True)
    metrics = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    req_source = Column(String(500), nullable=True)
    model = Column(String(100), nullable=True)
    # 是否已过期：0=有效, 1=已过期（用例保存修改后标记）
    is_expired = Column(Integer, nullable=False, default=0)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())


class ReviewSuggestionItem(Base):
    """AI 评审改进建议（独立实体）"""
    __tablename__ = "review_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    suggestion_uid = Column(String(20), nullable=False, unique=True, index=True)
    review_report_id = Column(Integer, nullable=False, index=True)
    project_id = Column(Integer, nullable=False, index=True)
    case_id = Column(Integer, nullable=False, index=True)
    field_path = Column(JSON, nullable=False)
    issue_type = Column(String(30), nullable=False)
    severity = Column(String(10), nullable=False)
    problem = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=False)
    sample_patch = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    handled_by = Column(String(100), nullable=True)
    handled_at = Column(DateTime(timezone=True), nullable=True)
    ignore_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    batch_id = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="running")
    total = Column(Integer, nullable=True)
    passed = Column(Integer, nullable=True)
    failed = Column(Integer, nullable=True)
    items = Column(JSON, nullable=True)
    logs = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)


class TestReport(Base):
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, nullable=False)
    pass_rate = Column(String(20), nullable=True)
    trends = Column(JSON, nullable=True)
    modules = Column(JSON, nullable=True)
    fails = Column(JSON, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    key = Column(String(200), nullable=False)
    value = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())