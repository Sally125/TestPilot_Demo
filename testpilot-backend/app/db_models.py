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
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())


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