import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db_models import Project, Requirement, TestCase, ExecutionRecord, \
    StabilityReport, ReviewReport, Execution, TestReport, SystemSetting, LoginProfile, \
    ReviewSuggestionItem


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
                     requirement_id: int = None, login_mode: str = "global",
                     login_role: str = None):
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
        script_path=script_path,
        login_mode=login_mode or "global",
        login_role=login_role
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


def update_test_case_login(db: Session, case_id: int, login_mode: str = None, login_role: str = None):
    """更新用例的登录态绑定"""
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if case:
        if login_mode is not None:
            case.login_mode = login_mode
        if login_role is not None:
            case.login_role = login_role
        db.commit()
        db.refresh(case)
    return case


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


def delete_requirement(db: Session, req_id: int):
    req = db.query(Requirement).filter(Requirement.id == req_id).first()
    if req:
        db.delete(req)
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
    return db.query(StabilityReport).filter(StabilityReport.project_id == project_id).order_by(StabilityReport.id.desc()).first()


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
    return db.query(ReviewReport).filter(ReviewReport.project_id == project_id).order_by(ReviewReport.id.desc()).first()


def get_review_report_by_id(db: Session, report_id: int):
    return db.query(ReviewReport).filter(ReviewReport.id == report_id).first()


# ==================== 评审建议 ====================

def create_review_suggestion(
    db: Session,
    suggestion_uid: str,
    review_report_id: int,
    project_id: int,
    case_id: int,
    field_path: list,
    issue_type: str,
    severity: str,
    problem: str,
    suggestion: str,
    sample_patch: dict = None,
):
    db_item = ReviewSuggestionItem(
        suggestion_uid=suggestion_uid,
        review_report_id=review_report_id,
        project_id=project_id,
        case_id=case_id,
        field_path=field_path,
        issue_type=issue_type,
        severity=severity,
        problem=problem,
        suggestion=suggestion,
        sample_patch=sample_patch,
        status="pending",
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_suggestions_by_review(db: Session, review_report_id: int, status: str = None, case_id: int = None):
    query = db.query(ReviewSuggestionItem).filter(
        ReviewSuggestionItem.review_report_id == review_report_id
    )
    if status:
        query = query.filter(ReviewSuggestionItem.status == status)
    if case_id:
        query = query.filter(ReviewSuggestionItem.case_id == case_id)
    return query.order_by(ReviewSuggestionItem.id.asc()).all()


def get_suggestion_by_uid(db: Session, suggestion_uid: str):
    return db.query(ReviewSuggestionItem).filter(
        ReviewSuggestionItem.suggestion_uid == suggestion_uid
    ).first()


def get_suggestions_by_case(db: Session, case_id: int, status: str = None):
    query = db.query(ReviewSuggestionItem).filter(
        ReviewSuggestionItem.case_id == case_id
    )
    if status:
        query = query.filter(ReviewSuggestionItem.status == status)
    return query.order_by(ReviewSuggestionItem.id.asc()).all()


def update_suggestion_status(
    db: Session,
    suggestion_uid: str,
    status: str,
    handled_by: str = None,
    ignore_reason: str = None,
):
    item = db.query(ReviewSuggestionItem).filter(
        ReviewSuggestionItem.suggestion_uid == suggestion_uid
    ).first()
    if not item:
        return None
    item.status = status
    if handled_by:
        item.handled_by = handled_by
    item.handled_at = datetime.datetime.now(datetime.timezone.utc)
    if ignore_reason is not None:
        item.ignore_reason = ignore_reason
    db.commit()
    db.refresh(item)
    return item


def update_test_case_review_status(db: Session, case_id: int, review_status: str):
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if case:
        case.review_status = review_status
        db.commit()
        db.refresh(case)
    return case


def update_case_with_suggestion(
    db: Session,
    case_id: int,
    update_fields: dict,
    expected_version: int,
    suggestion_uid: str | None = None,
    handled_by: str | None = None,
) -> tuple:
    """
    事务性更新用例并联动建议状态。
    返回 (更新后的用例, 错误信息)。错误信息为 None 表示成功。
    """
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        return None, "CASE_NOT_FOUND"

    # 乐观锁校验
    if case.version != expected_version:
        return None, "VERSION_CONFLICT"

    try:
        # 1. 更新用例字段
        for key, value in update_fields.items():
            if hasattr(case, key) and value is not None:
                setattr(case, key, value)

        # 2. 版本号自增
        case.version += 1

        # 3. 评审状态流转
        case.review_status = "modified_pending_review"

        # 4. 建议状态回写
        if suggestion_uid:
            suggestion = db.query(ReviewSuggestionItem).filter(
                ReviewSuggestionItem.suggestion_uid == suggestion_uid
            ).first()
            if suggestion:
                suggestion.status = "resolved"
                suggestion.handled_by = handled_by
                suggestion.handled_at = datetime.datetime.now(datetime.timezone.utc)

                # 5. 标记评审报告过期
                db.query(ReviewReport).filter(
                    ReviewReport.id == suggestion.review_report_id
                ).update({ReviewReport.is_expired: 1})

        db.commit()
        db.refresh(case)
        return case, None

    except Exception as e:
        db.rollback()
        return None, f"TRANSACTION_ERROR: {e}"


def create_execution(db: Session, project_id: int, batch_id: str, total: int = 0):
    db_exec = Execution(
        project_id=project_id,
        batch_id=batch_id,
        total=total,
        passed=0,
        failed=0,
        status="running",
        logs=[],
        started_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(db_exec)
    db.commit()
    db.refresh(db_exec)
    return db_exec


def add_execution_log(db: Session, exec_id: int, level: str, message: str):
    from sqlalchemy.orm.attributes import flag_modified
    exec_record = db.query(Execution).filter(Execution.id == exec_id).first()
    if exec_record:
        if exec_record.logs is None:
            exec_record.logs = []
        exec_record.logs.append({
            "level": level,
            "message": message,
            "time": datetime.datetime.now().isoformat()
        })
        # SQLAlchemy 的 JSON 列不会自动检测原地变更，需显式标记
        flag_modified(exec_record, "logs")
        db.commit()
        db.refresh(exec_record)
    return exec_record


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


def delete_execution(db: Session, exec_id: int):
    exec_record = db.query(Execution).filter(Execution.id == exec_id).first()
    if exec_record:
        # 同时删除关联的测试报告
        report = db.query(TestReport).filter(TestReport.execution_id == exec_id).first()
        if report:
            db.delete(report)
        db.delete(exec_record)
        db.commit()
        return True
    return False


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


# ==================== 登录态配置 ====================

def get_login_profiles(db: Session, project_id: int):
    """获取项目的所有登录态配置（按创建时间排序）"""
    return db.query(LoginProfile).filter(LoginProfile.project_id == project_id) \
        .order_by(LoginProfile.id.asc()).all()


def get_login_profile(db: Session, profile_id: int):
    return db.query(LoginProfile).filter(LoginProfile.id == profile_id).first()


def get_default_login_profile(db: Session, project_id: int):
    """获取项目的默认登录态"""
    return db.query(LoginProfile).filter(
        LoginProfile.project_id == project_id,
        LoginProfile.is_default == 1
    ).first()


def count_login_profiles(db: Session, project_id: int) -> int:
    """统计项目的登录态数量（不含匿名）"""
    return db.query(LoginProfile).filter(LoginProfile.project_id == project_id).count()


def create_login_profile(db: Session, project_id: int, name: str, role: str,
                         username: str = None, password: str = None,
                         storage_state_path: str = None, valid_days: int = 7,
                         is_default: bool = False,
                         login_url: str = None,
                         username_selector: str = None, username_selector_type: str = None,
                         password_selector: str = None, password_selector_type: str = None,
                         submit_selector: str = None, submit_selector_type: str = None,
                         success_indicator: str = None, success_indicator_type: str = None,
                         script_mode: str = "form", custom_script: str = None):
    valid_until = None
    if storage_state_path and valid_days > 0:
        valid_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=valid_days)
    # 如果设为默认，先清除其他默认
    if is_default:
        db.query(LoginProfile).filter(
            LoginProfile.project_id == project_id,
            LoginProfile.is_default == 1
        ).update({LoginProfile.is_default: 0})
    status = "valid" if storage_state_path else "ungenerated"
    db_profile = LoginProfile(
        project_id=project_id,
        name=name,
        role=role,
        username=username,
        password=password,
        storage_state_path=storage_state_path,
        valid_days=valid_days,
        valid_until=valid_until,
        status=status,
        is_default=1 if is_default else 0,
        login_url=login_url,
        username_selector=username_selector,
        username_selector_type=username_selector_type,
        password_selector=password_selector,
        password_selector_type=password_selector_type,
        submit_selector=submit_selector,
        submit_selector_type=submit_selector_type,
        success_indicator=success_indicator,
        success_indicator_type=success_indicator_type,
        script_mode=script_mode or "form",
        custom_script=custom_script
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_login_profile(db: Session, profile_id: int, **kwargs):
    profile = db.query(LoginProfile).filter(LoginProfile.id == profile_id).first()
    if not profile:
        return None
    # 处理 is_default：设为默认时清除其他默认
    if kwargs.get("is_default"):
        db.query(LoginProfile).filter(
            LoginProfile.project_id == profile.project_id,
            LoginProfile.is_default == 1,
            LoginProfile.id != profile_id
        ).update({LoginProfile.is_default: 0})
    # 处理 validDays：更新有效期
    if "validDays" in kwargs and kwargs["validDays"] is not None:
        profile.valid_days = kwargs["validDays"]
        if profile.storage_state_path and profile.valid_days > 0:
            profile.valid_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=profile.valid_days)
    # 处理 storageStatePath：更新时重新计算有效期
    if "storageStatePath" in kwargs and kwargs["storageStatePath"]:
        if profile.valid_days > 0:
            profile.valid_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=profile.valid_days)
        profile.status = "valid"
    # 字段映射（驼峰转下划线）
    field_map = {
        "name": "name", "role": "role", "username": "username",
        "password": "password", "storageStatePath": "storage_state_path",
        "status": "status", "isDefault": "is_default",
        "loginUrl": "login_url",
        "usernameSelector": "username_selector", "usernameSelectorType": "username_selector_type",
        "passwordSelector": "password_selector", "passwordSelectorType": "password_selector_type",
        "submitSelector": "submit_selector", "submitSelectorType": "submit_selector_type",
        "successIndicator": "success_indicator", "successIndicatorType": "success_indicator_type",
        "scriptMode": "script_mode", "customScript": "custom_script",
    }
    for key, value in kwargs.items():
        if key in ("validDays",):
            continue
        col = field_map.get(key, key)
        if hasattr(profile, col):
            if col == "is_default":
                setattr(profile, col, 1 if value else 0)
            else:
                setattr(profile, col, value)
    db.commit()
    db.refresh(profile)
    return profile


def delete_login_profile(db: Session, profile_id: int):
    profile = db.query(LoginProfile).filter(LoginProfile.id == profile_id).first()
    if profile:
        db.delete(profile)
        db.commit()
        return True
    return False