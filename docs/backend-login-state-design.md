# 后端技术文档：项目登录态强校验与脚本生成前置拦截

## 1. 背景与目标

### 1.1 问题
当前测试用例脚本生成阶段（`generate_scripts`）在调 AI 生成 Playwright 脚本时，AI 凭需求文本"想象"页面 DOM 结构，生成的 selector 常与真实页面不符（如 `getByPlaceholder('任务名称')`，实际页面并无此元素），导致脚本执行时 30s 超时失败。

后续计划引入"基于真实 DOM 快照生成脚本"的优化（见第 6 节），但该优化依赖项目的 `storageState` 才能访问受保护页面抓取真实 DOM。当前 `storageState` 的配置和生成时机晚于脚本生成阶段，存在时序缺口。

### 1.2 目标
- 在数据模型层标记项目是否需要登录态
- 在脚本生成入口强拦截：项目需要登录态但未生成会话时，拒绝生成并返回明确错误
- 为前端提供查询接口，支持前端同步展示登录态配置状态
- 为后续 DOM 快照优化铺路：透传 `storage_state_path` 给脚本生成阶段

### 1.3 时序对照
```
当前流程：
1. 需求分析
2. 测试用例设计
3. 用户确认用例
4. 脚本生成（generate_scripts）  ← 问题点：无 storageState，AI 凭想象生成
5. 稳定性检测
6. 确认登录态
7. 执行测试（run_script）        ← 此处才有 storageState

目标流程：
0. 项目创建（创建时配置登录态并生成会话）  ← 新增前置
1. 需求分析
2. 测试用例设计
3. 用户确认用例
4. 脚本生成（拦截校验 + DOM 快照）        ← 拦截 + 优化
5. 稳定性检测
6. 确认登录态
7. 执行测试
```

---

## 2. 数据模型变更

### 2.1 Project 表新增字段

文件：`app/db_models.py`

```python
class Project(Base):
    __tablename__ = "projects"

    # 既有字段...
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    app_url = Column(String(500), nullable=True)
    dim = Column(String(100), nullable=True)
    tech_stack = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ===== 新增字段 =====
    # 是否需要登录态：1=需要登录（测试受保护功能），0=无需登录（测试登录功能本身/公开页面）
    requires_login = Column(Integer, nullable=False, default=1)
```

### 2.2 字段语义

| 字段值 | 含义 | 创建时登录配置 | 后续脚本生成行为 |
|--------|------|----------------|------------------|
| `1`（默认） | 项目测试受保护功能，需要登录态 | 必填登录配置 | 拦截校验：无已生成会话则拒绝 |
| `0` | 项目测试登录功能本身，或公开页面 | 跳过登录配置 | 不拦截，匿名抓 DOM |

### 2.3 数据库迁移

SQLite 数据库，直接通过 SQLAlchemy 建表逻辑处理。对已存在的项目，`requires_login` 默认为 `1`（保守策略，已建项目默认按"需要登录"处理）。

---

## 3. API 变更

### 3.1 项目创建/更新接口

#### POST `/api/projects`

请求体新增字段：

```json
{
  "name": "考公大师",
  "description": "...",
  "appUrl": "http://localhost:3001",
  "dim": "web",
  "requiresLogin": 1
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requiresLogin | int | 是 | 1=需要登录，0=无需登录 |

后端校验逻辑：
- `requiresLogin == 1` 时，**不强制**请求体携带登录配置（登录态通过独立接口创建）
- `requiresLogin == 1` 时，若同时携带登录配置（见 3.2），则一并创建 LoginProfile

#### PUT `/api/projects/{project_id}`

支持更新 `requires_login` 字段。

### 3.2 登录态配置接口（复用现有）

项目创建时若用户填了登录配置，后端链式调用现有接口：

#### POST `/api/projects/{project_id}/login-profiles`

请求体（与现有接口一致）：

```json
{
  "name": "默认管理员",
  "role": "admin",
  "username": "huangkx1225@163.com",
  "password": "123456",
  "loginUrl": "http://localhost:3001/login",
  "usernameSelector": "getByRole('textbox', { name: '邮箱' })",
  "usernameSelectorType": "locator",
  "passwordSelector": "getByRole('textbox', { name: '密码' })",
  "passwordSelectorType": "locator",
  "submitSelector": "getByRole('button', { name: '登录' })",
  "submitSelectorType": "locator",
  "successIndicator": "/dashboard",
  "successIndicatorType": "url",
  "scriptMode": "form",
  "customScript": null,
  "isDefault": true,
  "validDays": 7
}
```

#### POST `/api/login-profiles/{profile_id}/generate-session`

生成 storageState 文件。项目创建时链式调用此接口预生成会话。

### 3.3 项目详情接口

#### GET `/api/projects/{project_id}`

响应体新增字段：

```json
{
  "id": 1,
  "name": "考公大师",
  "appUrl": "http://localhost:3001",
  "requiresLogin": 1,
  "loginStateStatus": {
    "hasProfile": true,
    "hasSession": true,
    "sessionExpired": false,
    "defaultProfileId": 2
  }
}
```

`loginStateStatus` 由后端聚合计算：
- `hasProfile`: 是否存在非匿名的 LoginProfile
- `hasSession`: 默认 profile 是否有 `storage_state_path` 且文件存在
- `sessionExpired`: 会话是否已过期（`valid_until < now`）
- `defaultProfileId`: 默认 profile 的 ID（无则 null）

### 3.4 脚本生成接口（核心拦截点）

#### POST `/api/generate`

请求体新增字段：

```json
{
  "test_cases": [...],
  "app_url": "http://localhost:3001",
  "project_id": 1
}
```

| 新增字段 | 类型 | 必填 | 说明 |
|----------|------|------|------|
| project_id | int | 是 | 用于查询项目的登录态配置 |

**拦截逻辑**（新增）：

```python
@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, db: Session = Depends(get_db)) -> GenerateResponse:
    # ===== 新增：登录态前置拦截 =====
    if req.project_id:
        project = get_project(db, req.project_id)
        if project and project.requires_login == 1:
            # 检查是否存在已生成会话的登录态
            default_profile = get_default_login_profile(db, req.project_id)
            if not default_profile or not default_profile.storage_state_path:
                raise HTTPException(
                    status_code=400,
                    detail="项目需要登录态，但尚未生成会话。请先在「登录态配置」中生成会话后再生成脚本。"
                )
            # 检查会话是否过期
            if default_profile.valid_until and default_profile.valid_until < datetime.datetime.now(datetime.timezone.utc):
                raise HTTPException(
                    status_code=400,
                    detail="项目登录态会话已过期，请重新生成会话后再生成脚本。"
                )

    # 透传 storage_state_path 给脚本生成（为后续 DOM 快照优化准备）
    storage_state_path = None
    if req.project_id:
        default_profile = get_default_login_profile(db, req.project_id)
        if default_profile and default_profile.storage_state_path:
            storage_state_path = default_profile.storage_state_path

    ai = AIService()
    return await ai.generate_scripts(
        req.test_cases,
        req.app_url,
        storage_state_path=storage_state_path  # 新增参数
    )
```

#### POST `/api/generate/stream`

同步增加拦截逻辑（与 `/generate` 一致）。

### 3.5 GenerateRequest 模型变更

文件：`app/models.py`

```python
class GenerateRequest(BaseModel):
    test_cases: list[DesignedTestCase]
    app_url: str = ""
    project_id: int | None = None  # 新增
```

---

## 4. CRUD 层变更

### 4.1 新增/修改的函数

文件：`app/crud.py`

```python
def create_project(db: Session, name: str, description: str = None, app_url: str = None,
                   dim: str = None, tech_stack: str = None,
                   requires_login: int = 1):  # 新增参数
    db_project = Project(
        name=name,
        description=description,
        app_url=app_url,
        dim=dim,
        tech_stack=tech_stack,
        requires_login=requires_login  # 新增
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
    # 既有逻辑支持 kwargs 透传，无需改动，requires_login 自动支持
    ...


def get_project_login_state_status(db: Session, project_id: int) -> dict:
    """聚合查询项目的登录态配置状态（供 GET /projects/{id} 使用）"""
    profiles = get_login_profiles(db, project_id)
    configured = [p for p in profiles if p.id != 'anonymous']
    default = get_default_login_profile(db, project_id)

    has_session = False
    session_expired = False
    if default and default.storage_state_path:
        # 检查文件是否存在
        from pathlib import Path
        has_session = Path(default.storage_state_path).exists()
        # 检查是否过期
        if default.valid_until:
            now = datetime.datetime.now(datetime.timezone.utc)
            expired = default.valid_until
            # 统一时区比较
            if expired.tzinfo is None:
                expired = expired.replace(tzinfo=datetime.timezone.utc)
            session_expired = expired < now

    return {
        "hasProfile": len(configured) > 0,
        "hasSession": has_session,
        "sessionExpired": session_expired,
        "defaultProfileId": default.id if default else None
    }
```

---

## 5. AIService 层变更

### 5.1 generate_scripts 签名扩展

文件：`app/services.py`

```python
async def generate_scripts(
    self,
    test_cases: list[DesignedTestCase],
    app_url: str = "",
    storage_state_path: str | None = None,  # 新增参数
) -> GenerateResponse:
    """脚本生成：测试用例 → Playwright 脚本（含稳定性检测）"""
    from .stability_checker import StabilityChecker

    # ...（既有 tc_json、test_account、app_name 逻辑不变）

    base_prompt = GENERATE_PROMPT.format(
        test_cases_json=tc_json,
        app_name=app_name,
        app_url=app_url or "未提供",
        login_url=s.login_url or "未提供",
        test_account=test_account,
        test_username=s.test_username or "",
        test_password=s.test_password or "",
        # page_context 暂时留空，第 6 节 DOM 快照优化时填充
        page_context="# 页面快照（暂未启用）",
    )

    # ...（既有 AI 调用、稳定性检测逻辑不变）
```

### 5.2 为后续 DOM 快照预留

`storage_state_path` 参数当前仅透传不使用，为第 6 节优化准备。

---

## 6. 后续优化：基于真实 DOM 快照的脚本生成（二期，本次不实施）

### 6.1 新增模块 `app/dom_snapshot.py`

```python
"""页面 DOM 快照抓取器：为 AI 脚本生成提供真实页面上下文"""
from __future__ import annotations
import logging
from typing import Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


async def capture_page_context(
    url: str,
    storage_state_path: Optional[str] = None,
    timeout_ms: int = 15000,
) -> dict:
    """
    访问目标 URL，抓取页面可访问性快照和关键交互元素清单。

    :param url: 目标页面 URL
    :param storage_state_path: storageState 文件路径（用于登录态注入）
    :param timeout_ms: 超时时间
    :return: {
        "url", "title", "accessibility_tree",
        "buttons", "inputs", "links", "error"
    }
    """
    result = {"url": url, "error": None}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ctx_kwargs = {}
            if storage_state_path:
                ctx_kwargs["storage_state"] = storage_state_path
            context = await browser.new_context(**ctx_kwargs)
            page = await context.new_page()

            await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass

            result["title"] = await page.title()

            # 1. 可访问性树（精简）
            snap = await page.accessibility.snapshot()
            result["accessibility_tree"] = _simplify_a11y(snap, depth=0, max_depth=4)

            # 2. 所有按钮
            buttons = await page.get_by_role("button").all()
            result["buttons"] = []
            for b in buttons[:30]:
                try:
                    name = (await b.inner_text()).strip()[:50]
                    if name:
                        result["buttons"].append({"name": name})
                except Exception:
                    pass

            # 3. 所有输入框
            inputs = await page.locator("input,textarea,select").all()
            result["inputs"] = []
            for inp in inputs[:30]:
                try:
                    placeholder = await inp.get_attribute("placeholder") or ""
                    inp_type = await inp.get_attribute("type") or "text"
                    aria_label = await inp.get_attribute("aria-label") or ""
                    label_id = await inp.get_attribute("id") or ""
                    label_text = ""
                    if label_id:
                        label_loc = page.locator(f'label[for="{label_id}"]')
                        if await label_loc.count() > 0:
                            label_text = (await label_loc.inner_text()).strip()[:50]
                    result["inputs"].append({
                        "placeholder": placeholder[:50],
                        "type": inp_type,
                        "label": label_text or aria_label,
                    })
                except Exception:
                    pass

            # 4. 所有链接
            links = await page.get_by_role("link").all()
            result["links"] = []
            for lk in links[:20]:
                try:
                    name = (await lk.inner_text()).strip()[:30]
                    href = await lk.get_attribute("href") or ""
                    if name:
                        result["links"].append({"name": name, "href": href[:80]})
                except Exception:
                    pass

            await browser.close()
    except Exception as e:
        logger.warning(f"抓取页面快照失败: {type(e).__name__}: {e}")
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def _simplify_a11y(node, depth, max_depth):
    """递归精简 a11y 树，只保留 role+name，限制深度"""
    if not node or depth > max_depth:
        return ""
    role = node.get("role", "")
    name = (node.get("name") or "").strip()[:60]
    line = f"{'  ' * depth}- {role}" + (f' "{name}"' if name else "") + "\n"
    for child in node.get("children", [])[:15]:
        line += _simplify_a11y(child, depth + 1, max_depth)
    return line


def format_snapshot_for_prompt(snap: dict) -> str:
    """把快照格式化为 Prompt 友好的文本段落"""
    if snap.get("error"):
        return f"# 页面快照（抓取失败：{snap['error']}，请基于需求文本推断）"

    parts = [f"# 目标页面真实 DOM 上下文（URL: {snap.get('url')}）"]
    parts.append(f"页面标题: {snap.get('title', '')}\n")

    if snap.get("accessibility_tree"):
        parts.append("## 可访问性树（角色+名称）")
        parts.append("```")
        parts.append(snap["accessibility_tree"][:3000])
        parts.append("```\n")

    if snap.get("buttons"):
        parts.append("## 页面上的所有按钮（生成 click 选择器时参考）")
        for b in snap["buttons"]:
            parts.append(f'- getByRole("button", {{ name: "{b["name"]}" }})')
        parts.append("")

    if snap.get("inputs"):
        parts.append("## 页面上的所有输入框（生成 fill 选择器时参考）")
        for i in snap["inputs"]:
            hint = []
            if i.get("label"):
                hint.append(f'getByLabel("{i["label"]}")')
            if i.get("placeholder"):
                hint.append(f'getByPlaceholder("{i["placeholder"]}")')
            parts.append(f"- {' / '.join(hint) or '无 label/placeholder'} (type={i['type']})")
        parts.append("")

    if snap.get("links"):
        parts.append("## 导航链接")
        for l in snap["links"]:
            parts.append(f'- {l["name"]} -> {l["href"]}')
        parts.append("")

    parts.append("## 重要提示")
    parts.append("- 上述元素为 page.goto 后立即可见的元素")
    parts.append("- 若目标表单字段不在列表中，说明它需要先点击入口按钮（如'+ 添加任务'）才显示")
    parts.append("- 必须使用上面列出的真实 selector，不要凭空想象")

    return "\n".join(parts)
```

### 6.2 services.py 集成

```python
async def generate_scripts(
    self,
    test_cases: list[DesignedTestCase],
    app_url: str = "",
    storage_state_path: str | None = None,
) -> GenerateResponse:
    # ...（既有逻辑）

    # ===== 二期：抓取真实页面快照 =====
    from .dom_snapshot import capture_page_context, format_snapshot_for_prompt
    page_context_text = ""
    if app_url and app_url != "未提供":
        try:
            snap = await capture_page_context(
                url=app_url,
                storage_state_path=storage_state_path,
                timeout_ms=15000,
            )
            page_context_text = format_snapshot_for_prompt(snap)
        except Exception as e:
            logger.warning(f"页面快照抓取异常（降级为纯文本生成）: {e}")
            page_context_text = "# 页面快照（抓取失败，请基于需求文本推断）"
    else:
        page_context_text = "# 页面快照（未提供 app_url，请基于需求文本推断）"

    base_prompt = GENERATE_PROMPT.format(
        # ...（既有参数）
        page_context=page_context_text,
    )
```

### 6.3 prompts.py 变更

GENERATE_PROMPT 新增 `{page_context}` 占位符：

```python
GENERATE_PROMPT = """根据以下测试用例，生成 Playwright 测试脚本。

# 测试用例
{test_cases_json}

# 应用信息
- 名称: {app_name}
- URL: {app_url}
- 登录URL: {login_url}
- 账号: {test_account}

{page_context}

# 核心规则（必须遵守）
...（既有规则）
"""
```

---

## 7. 实施步骤

### 7.1 一期（本次实施）

| 步骤 | 文件 | 改动 |
|------|------|------|
| 1 | `app/db_models.py` | Project 表新增 `requires_login` 字段 |
| 2 | `app/models.py` | ProjectCreate 新增 `requiresLogin` 字段；GenerateRequest 新增 `project_id` 字段 |
| 3 | `app/crud.py` | create_project 支持 requires_login；新增 get_project_login_state_status |
| 4 | `app/routes.py` | POST /projects 支持 requiresLogin；GET /projects/{id} 返回 loginStateStatus；POST /generate 加拦截 |
| 5 | `app/services.py` | generate_scripts 签名新增 storage_state_path 参数 |
| 6 | `app/prompts.py` | GENERATE_PROMPT 新增 `{page_context}` 占位符（一期填空字符串） |

### 7.2 二期（后续）

| 步骤 | 文件 | 改动 |
|------|------|------|
| 1 | `app/dom_snapshot.py` | 新建模块 |
| 2 | `app/services.py` | generate_scripts 调 capture_page_context 填充 page_context |
| 3 | 依赖 | `pip install playwright` + `playwright install chromium` |

---

## 8. 错误码约定

| HTTP 状态码 | 场景 | detail 示例 |
|-------------|------|-------------|
| 400 | 项目需要登录态但未生成会话 | `项目需要登录态，但尚未生成会话。请先在「登录态配置」中生成会话后再生成脚本。` |
| 400 | 项目登录态会话已过期 | `项目登录态会话已过期，请重新生成会话后再生成脚本。` |
| 400 | 项目名称重复 | 既有逻辑 |
| 404 | 项目不存在 | 既有逻辑 |

---

## 9. 测试用例

### 9.1 接口测试

| 用例 | 前置条件 | 操作 | 预期 |
|------|----------|------|------|
| 创建需要登录的项目 | 无 | POST /projects，requiresLogin=1 | 201，返回项目 ID |
| 创建无需登录的项目 | 无 | POST /projects，requiresLogin=0 | 201，返回项目 ID |
| 脚本生成-无会话拦截 | 项目 requiresLogin=1，无 LoginProfile | POST /generate | 400，detail 提示生成会话 |
| 脚本生成-会话过期拦截 | 项目 requiresLogin=1，profile.valid_until 已过期 | POST /generate | 400，detail 提示会话过期 |
| 脚本生成-正常 | 项目 requiresLogin=1，profile 有效 | POST /generate | 200，返回脚本 |
| 脚本生成-无需登录 | 项目 requiresLogin=0 | POST /generate | 200，不拦截 |
| 查询项目登录态状态 | 项目有默认 profile 且会话有效 | GET /projects/{id} | loginStateStatus.hasSession=true |
