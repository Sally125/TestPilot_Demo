from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db_models import Project, Requirement, TestCase, ExecutionRecord, \
    StabilityReport, ReviewReport, Execution, TestReport, SystemSetting


def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()


def get_project_by_name(db: Session, name: str):
    return db.query(Project).filter(Project.name == name).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).offset(skip).limit(limit).all()


def create_project(db: Session, name: str, description: str = None, app_url: str = None,
                   dim: str = None, tech_stack: str = None):
    db_project = Project(
        name=name,
        description=description,
        app_url=app_url,
        dim=dim,
        tech_stack=tech_stack
    )
    db.add(db_project)
    try:
        db.commit()
        db.refresh(db_project)
        return db_project
    except IntegrityError:
        db.rollback()
        return None


def update_project(db: Session, project_id: int, **kwargs):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        db.commit()
        db.refresh(project)
    return project


def delete_project(db: Session, project_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
        return True
    return False


def create_requirement(db: Session, project_id: int, title: str, content: str, analysis_result: dict = None):
    db_req = Requirement(
        project_id=project_id,
        title=title,
        content=content,
        analysis_result=analysis_result
    )
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return db_req


def get_requirements(db: Session, project_id: int):
    return db.query(Requirement).filter(Requirement.project_id == project_id).all()


def get_requirement(db: Session, req_id: int):
    return db.query(Requirement).filter(Requirement.id == req_id).first()


def update_requirement_analysis(db: Session, req_id: int, analysis_result: dict):
    req = db.query(Requirement).filter(Requirement.id == req_id).first()
    if req:
        req.analysis_result = analysis_result
        db.commit()
        db.refresh(req)
    return req


def create_test_case(db: Session, project_id: int, title: str, module: str = None,
                     priority: str = "P1", precondition: str = None, steps: list = None,
                     expected: str = None, script: str = None, script_path: str = None,
                     requirement_id: int = None):
    db_case = TestCase(
        project_id=project_id,
        requirement_id=requirement_id,
        title=title,
        module=module,
        priority=priority,
        precondition=precondition,
        steps=steps or [],
        expected=expected,
        script=script,
        script_path=script_path
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


def get_test_cases(
    db: Session, 
    project_id: int, 
    module: str = None, 
    priority: str = None, 
    status: str = None, 
    keyword: str = None,
    page: int = 1,
    page_size: int = 20
):
    query = db.query(TestCase).filter(TestCase.project_id == project_id)
    
    if module:
        query = query.filter(TestCase.module == module)
    if priority:
        query = query.filter(TestCase.priority == priority)
    if status:
        query = query.filter(TestCase.status == status)
    if keyword:
        query = query.filter(
            TestCase.title.contains(keyword) | 
            (TestCase.precondition != None and TestCase.precondition.contains(keyword)) |
            (TestCase.expected != None and TestCase.expected.contains(keyword))
        )
    
    total = query.count()
    
    offset = (page - 1) * page_size
    cases = query.offset(offset).limit(page_size).all()
    
    return cases, total


def get_test_case(db: Session, case_id: int):
    return db.query(TestCase).filter(TestCase.id == case_id).first()


def update_test_case_status(db: Session, case_id: int, status: str):
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if case:
        case.status = status
        db.commit()
        db.refresh(case)
    return case


def delete_test_case(db: Session, case_id: int):
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if case:
        db.delete(case)
        db.commit()
        return True
    return False


def create_execution_record(db: Session, project_id: int, case_id: int, passed: bool,
                            duration_ms: int = None, error: str = None, screenshots: list = None):
    db_record = ExecutionRecord(
        project_id=project_id,
        case_id=case_id,
        passed=int(passed),
        duration_ms=duration_ms,
        error=error,
        screenshots=screenshots or []
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_execution_records(db: Session, project_id: int = None, case_id: int = None):
    query = db.query(ExecutionRecord)
    if project_id:
        query = query.filter(ExecutionRecord.project_id == project_id)
    if case_id:
        query = query.filter(ExecutionRecord.case_id == case_id)
    return query.order_by(ExecutionRecord.executed_at.desc()).all()


def create_stability_report(db: Session, project_id: int, checks: dict, issues: list, scores: dict, overall_score: int):
    db_report = StabilityReport(
        project_id=project_id,
        checks=checks,
        issues=issues,
        scores=scores,
        overall_score=overall_score
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_stability_report(db: Session, project_id: int):
    return db.query(StabilityReport).filter(StabilityReport.project_id == project_id).first()


def create_review_report(db: Session, project_id: int, score: int, metrics: dict, suggestions: list,
                         req_source: str = None, model: str = None):
    db_report = ReviewReport(
        project_id=project_id,
        score=score,
        metrics=metrics,
        suggestions=suggestions,
        req_source=req_source,
        model=model
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_review_report(db: Session, project_id: int):
    return db.query(ReviewReport).filter(ReviewReport.project_id == project_id).first()


def create_execution(db: Session, project_id: int, batch_id: str, total: int = 0):
    db_exec = Execution(
        project_id=project_id,
        batch_id=batch_id,
        total=total,
        passed=0,
        failed=0,
        status="running"
    )
    db.add(db_exec)
    db.commit()
    db.refresh(db_exec)
    return db_exec


def update_execution(db: Session, exec_id: int, **kwargs):
    exec_record = db.query(Execution).filter(Execution.id == exec_id).first()
    if exec_record:
        for key, value in kwargs.items():
            if hasattr(exec_record, key):
                setattr(exec_record, key, value)
        db.commit()
        db.refresh(exec_record)
    return exec_record


def get_execution(db: Session, exec_id: int):
    return db.query(Execution).filter(Execution.id == exec_id).first()


def get_executions(db: Session, project_id: int = None):
    query = db.query(Execution)
    if project_id:
        query = query.filter(Execution.project_id == project_id)
    return query.order_by(Execution.started_at.desc()).all()


def create_test_report(db: Session, execution_id: int, pass_rate: str, trends: dict = None,
                       modules: dict = None, fails: list = None):
    db_report = TestReport(
        execution_id=execution_id,
        pass_rate=pass_rate,
        trends=trends or {},
        modules=modules or {},
        fails=fails or []
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_test_report(db: Session, execution_id: int):
    return db.query(TestReport).filter(TestReport.execution_id == execution_id).first()


def get_setting(db: Session, category: str, key: str):
    return db.query(SystemSetting).filter(
        SystemSetting.category == category,
        SystemSetting.key == key
    ).first()


def set_setting(db: Session, category: str, key: str, value, description: str = None):
    setting = db.query(SystemSetting).filter(
        SystemSetting.category == category,
        SystemSetting.key == key
    ).first()
    if setting:
        setting.value = value
        if description:
            setting.description = description
    else:
        setting = SystemSetting(
            category=category,
            key=key,
            value=value,
            description=description
        )
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def get_settings_by_category(db: Session, category: str):
    return db.query(SystemSetting).filter(SystemSetting.category == category).all()


def get_all_settings(db: Session):
    return db.query(SystemSetting).all()