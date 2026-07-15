# 前端技术文档：项目创建登录态配置与多重防线

## 1. 背景与目标

### 1.1 问题
当前项目创建表单（[L1845-1912](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html#L1845)）只有项目名称、描述、测试维度、应用 URL、测试浏览器字段，**完全没有登录态配置**。

用户在后续脚本生成阶段触发时才发现登录态缺失，但此时脚本已生成且错误，浪费一轮 AI 调用。

### 1.2 目标
- 项目创建表单新增"登录需求"选择，引导用户明确项目是否需要登录态
- 选择"需要登录"时展开登录配置区域，支持表单模式和自定义脚本模式
- 项目创建后链式调用后端接口创建登录态 + 生成会话
- 在用例确认、脚本生成等关键节点设置多重防线，避免漏配登录态导致错误脚本

### 1.3 多重防线总览
```
项目创建 ── 防线1：表单强校验登录配置（前端硬拦截）
    │
    ▼
用例设计完成 ── 防线4：预警提示（可跳过）
    │
    ▼
脚本生成 ── 防线3：后端硬拦截（前端展示错误并引导）
    │
    ▼
执行测试 ── 防线5：禁止执行（既有逻辑兜底）
```

---

## 2. 表单设计

### 2.1 表单结构

在现有 [新建项目表单](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html#L1845) 的"测试浏览器"之后追加"登录态配置"区域：

```
┌─ 新建测试项目 ─────────────────────────────┐
│                                              │
│  项目名称 *  [_______________________]       │
│  项目描述    [_______________________]       │
│  测试维度 *  [Web] [Mobile] [API] [混合]     │
│  应用 URL *  [http://localhost:3001______]   │
│  测试浏览器  [✓]Chromium [ ]Firefox           │
│                                              │
│  ─── 登录态配置（新增）───                    │
│  登录需求 *  ○ 需要登录（测试受保护功能）     │
│              ● 无需登录（测试登录/公开页面）  │
│                                              │
│  ─── 选中"需要登录"时展开以下字段 ───        │
│                                              │
│  登录页 URL  [http://localhost:3001/login_]  │
│  账号 *      [huangkx1225@163.com______]     │
│  密码 *      [_______________________]       │
│  有效期      [7] 天                          │
│                                              │
│  定位方式    [表单模式] [自定义脚本]          │
│                                              │
│  ─── 表单模式字段（默认）───                 │
│  用户名选择器  [getByRole('textbox',         │
│                 { name: '邮箱' })______]     │
│  选择器类型    [locator ▼]                   │
│  密码选择器    [getByRole('textbox',         │
│                 { name: '密码' })______]     │
│  选择器类型    [locator ▼]                   │
│  提交按钮      [getByRole('button',          │
│                 { name: '登录' })______]     │
│  选择器类型    [locator ▼]                   │
│  成功标志      [/dashboard_______________]   │
│  标志类型      [url ▼]                       │
│                                              │
│  ☐ 创建后立即生成会话（推荐，默认勾选）      │
│                                              │
│              [取消]  [创建项目]              │
└──────────────────────────────────────────────┘
```

### 2.2 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| 登录需求 | 单选 | 是 | 无需登录 | 控制是否展开登录配置区 |
| 登录页 URL | text | 条件必填 | 空 | 登录页地址 |
| 账号 | text | 条件必填 | 空 | 登录账号 |
| 密码 | password | 条件必填 | 空 | 登录密码 |
| 有效期 | number | 否 | 7 | storageState 有效天数 |
| 定位方式 | 切换按钮 | 是 | 表单模式 | form/custom |
| 用户名选择器 | text | 条件必填 | 推荐值 | 见 2.3 |
| 选择器类型 | select | 是 | locator | css/locator/placeholder |
| 密码选择器 | text | 条件必填 | 推荐值 | 见 2.3 |
| 提交按钮 | text | 条件必填 | 推荐值 | 见 2.3 |
| 成功标志 | text | 否 | /dashboard | 登录成功判断标志 |
| 标志类型 | select | 是 | url | url/css/placeholder/locator |
| 自定义脚本 | textarea | 条件必填 | 模板 | 仅 custom 模式显示 |
| 创建后生成会话 | checkbox | 否 | 勾选 | 是否链式触发生成会话 |

**条件必填规则**：当"登录需求=需要登录"时，登录页 URL、账号、密码为必填；定位方式相关字段根据模式必填。

### 2.3 推荐默认值

针对常见 Next.js/React 应用，预填推荐值降低用户填写成本：

| 字段 | 推荐值 | 选择器类型 |
|------|--------|------------|
| 用户名选择器 | `getByRole('textbox', { name: '邮箱' })` | locator |
| 密码选择器 | `getByRole('textbox', { name: '密码' })` | locator |
| 提交按钮 | `getByRole('button', { name: '登录' })` | locator |
| 成功标志 | `/dashboard` | url |

用户可修改，但 80% 场景开箱即用。

### 2.4 交互逻辑

```javascript
// 登录需求单选切换
function toggleLoginRequirement(needsLogin) {
  const configArea = document.getElementById('login-config-area');
  configArea.style.display = needsLogin ? 'block' : 'none';
}

// 定位方式切换（复用现有 switchLoginScriptMode 函数）
// 表单模式 / 自定义脚本模式切换
```

---

## 3. 前端逻辑变更

### 3.1 handleCreateProject 改造

文件：`AI测试智能体_TestPilot.html`，现有函数 [handleCreateProject](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html#L2270)

```javascript
async function handleCreateProject() {
  const name = document.getElementById('project-name-input').value.trim();
  if (!name) {
    showToast('请输入项目名称', 'warning');
    return;
  }

  const desc = document.getElementById('project-desc-input').value.trim();
  const appUrl = document.getElementById('project-app-url').value.trim();
  const selectedDims = document.querySelectorAll('.dimension-option.selected');
  const dim = Array.from(selectedDims).map(d => d.dataset.dim).join('+');

  // ===== 新增：登录需求 =====
  const needsLogin = document.querySelector('input[name="login-requirement"]:checked').value === 'yes';
  const generateSessionNow = document.getElementById('lp-generate-now').checked;

  // ===== 新增：防线1 - 表单强校验 =====
  let loginConfig = null;
  if (needsLogin) {
    const loginUrl = document.getElementById('lp-login-url').value.trim();
    const username = document.getElementById('lp-username').value.trim();
    const password = document.getElementById('lp-password').value.trim();
    if (!loginUrl || !username || !password) {
      showToast('选择"需要登录"后，登录页URL、账号、密码为必填项', 'warning');
      return;
    }
    loginConfig = collectLoginConfig();  // 收集表单配置
  }

  showLoading('创建项目中...');
  try {
    // 1. 创建项目
    const created = await TestPilotAPI.createProject({
      name, description: desc, appUrl, dim,
      requiresLogin: needsLogin ? 1 : 0
    });

    // 2. 需要登录时，链式创建登录态 + 生成会话
    if (needsLogin && loginConfig) {
      showLoading('创建登录态配置中...');
      const profile = await TestPilotAPI.createLoginProfile(created.id, loginConfig);

      if (generateSessionNow) {
        showLoading('正在生成登录会话（Playwright 自动登录）...');
        try {
          await TestPilotAPI.generateSession(profile.id);
          showToast('项目创建成功，登录会话已生成', 'success');
        } catch (sessionErr) {
          showToast(`项目已创建，但会话生成失败：${sessionErr.message}。可稍后在「登录态配置」中重试。`, 'warning');
        }
      } else {
        showToast('项目创建成功，请稍后在「登录态配置」中生成会话', 'success');
      }
    } else {
      showToast('项目创建成功');
    }

    // ...（既有 projectData.push 逻辑，新增 requiresLogin 字段）
    projectData.push({
      // ...既有字段
      requiresLogin: needsLogin ? 1 : 0,
    });

    currentProjectIdx = projectData.length - 1;
    closeCreateProjectModal();
    refreshProjectContent();
    switchPage('requirement');
  } catch (error) {
    showToast('创建失败: ' + error.message, 'danger');
  } finally {
    hideLoading();
  }
}

// 收集登录配置表单数据
function collectLoginConfig() {
  const scriptMode = document.getElementById('lp-mode-custom-btn').style.background.includes('var(--primary)') ? 'custom' : 'form';
  return {
    name: '默认登录态',
    role: 'default',
    username: document.getElementById('lp-username').value.trim(),
    password: document.getElementById('lp-password').value.trim(),
    loginUrl: document.getElementById('lp-login-url').value.trim(),
    validDays: parseInt(document.getElementById('lp-valid-days').value, 10) || 7,
    isDefault: true,
    // 表单模式字段
    usernameSelector: document.getElementById('lp-username-selector').value.trim() || null,
    usernameSelectorType: document.getElementById('lp-username-selector-type').value,
    passwordSelector: document.getElementById('lp-password-selector').value.trim() || null,
    passwordSelectorType: document.getElementById('lp-password-selector-type').value,
    submitSelector: document.getElementById('lp-submit-selector').value.trim() || null,
    submitSelectorType: document.getElementById('lp-submit-selector-type').value,
    successIndicator: document.getElementById('lp-success-indicator').value.trim() || null,
    successIndicatorType: document.getElementById('lp-success-indicator-type').value,
    // 自定义脚本模式字段
    scriptMode: scriptMode,
    customScript: scriptMode === 'custom' && document.getElementById('lp-custom-script')
      ? document.getElementById('lp-custom-script').value.trim() : null,
  };
}
```

### 3.2 脚本生成调用改造

文件：`AI测试智能体_TestPilot.html`，搜索 `generate_scripts` 或 `/generate` 的调用处

```javascript
// 调用脚本生成 API 时，新增 project_id 参数
async function callGenerateScripts(testCases, appUrl) {
  const projectId = getCurrentProjectId();
  const res = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      test_cases: testCases,
      app_url: appUrl,
      project_id: projectId  // 新增：供后端拦截校验
    })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '生成失败' }));
    // 防线3：后端拦截时，前端引导用户去配置登录态
    if (res.status === 400 && err.detail && err.detail.includes('登录态')) {
      const ok = confirm(`${err.detail}\n\n是否现在去配置登录态？`);
      if (ok) {
        showLoginConfig();  // 跳转登录态配置面板
      }
      throw new Error(err.detail);
    }
    throw new Error(err.detail || '生成失败');
  }
  return res.json();
}
```

### 3.3 防线4：用例确认预警

文件：`AI测试智能体_TestPilot.html`，搜索用例确认按钮的处理函数

```javascript
async function handleConfirmTestCases() {
  const project = projectData[currentProjectIdx];

  // 防线4：用例确认前预警
  if (project.requiresLogin === 1) {
    const status = await checkProjectLoginStateStatus(project.id);
    if (!status.hasSession) {
      const ok = confirm(
        '检测到项目需要登录态，但尚未生成会话。\n' +
        '继续确认将进入脚本生成阶段，届时会强制要求登录态。\n\n' +
        '是否现在去配置登录态？'
      );
      if (ok) {
        showLoginConfig();
        return;
      }
    }
  }

  // ...（继续既有确认逻辑）
}

// 查询项目登录态状态
async function checkProjectLoginStateStatus(projectId) {
  try {
    const project = await TestPilotAPI.getProject(projectId);
    return project.loginStateStatus || { hasSession: false };
  } catch (e) {
    return { hasSession: false };
  }
}
```

### 3.4 编辑项目表单同步

编辑项目表单（[edit-project-modal](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html#L1914)）也需同步增加"登录需求"字段，允许后续修改。

---

## 4. TestPilotAPI 新增/修改方法

文件：`AI测试智能体_TestPilot.html`，TestPilotAPI 对象

```javascript
const TestPilotAPI = {
  // ...既有方法

  async createProject(data) {
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)  // 现在包含 requiresLogin 字段
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: '创建失败' }));
      throw new Error(err.detail || '创建失败');
    }
    return res.json();
  },

  async getProject(projectId) {
    const res = await fetch(`${API_BASE}/projects/${projectId}`);
    if (!res.ok) throw new Error('获取项目失败');
    return res.json();  // 现在包含 requiresLogin 和 loginStateStatus
  },

  async createLoginProfile(projectId, data) {
    const res = await fetch(`${API_BASE}/projects/${projectId}/login-profiles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: '创建登录态失败' }));
      throw new Error(err.detail || '创建登录态失败');
    }
    return res.json();
  },

  async generateSession(profileId) {
    const res = await fetch(`${API_BASE}/login-profiles/${profileId}/generate-session`, {
      method: 'POST'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: '生成会话失败' }));
      throw new Error(err.detail || '生成会话失败');
    }
    return res.json();
  }
};
```

---

## 5. UI 组件细节

### 5.1 登录需求单选

```html
<div class="form-group">
  <label class="input-label">登录需求 *</label>
  <div style="display:flex;gap:16px;margin-top:4px;">
    <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:13px;">
      <input type="radio" name="login-requirement" value="yes" onchange="toggleLoginRequirement(true)">
      需要登录（测试受保护功能）
    </label>
    <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:13px;">
      <input type="radio" name="login-requirement" value="no" checked onchange="toggleLoginRequirement(false)">
      无需登录（测试登录/公开页面）
    </label>
  </div>
  <div style="font-size:11px;color:var(--ink-3);margin-top:4px;">
    测试登录功能本身或公开页面选"无需登录"；测试受保护功能选"需要登录"
  </div>
</div>
```

### 5.2 登录配置区（条件展开）

```html
<div id="login-config-area" style="display:none;border-top:1px solid var(--border);padding-top:16px;margin-top:16px;">
  <div style="font-size:13px;font-weight:600;margin-bottom:12px;color:var(--ink-1);">登录态配置</div>

  <!-- 基本信息 -->
  <div class="form-group">
    <label class="input-label">登录页 URL *</label>
    <input type="text" class="input-field" id="lp-login-url" placeholder="http://localhost:3001/login" />
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
    <div class="form-group">
      <label class="input-label">账号 *</label>
      <input type="text" class="input-field" id="lp-username" placeholder="登录账号" />
    </div>
    <div class="form-group">
      <label class="input-label">密码 *</label>
      <input type="password" class="input-field" id="lp-password" placeholder="登录密码" />
    </div>
  </div>
  <div class="form-group">
    <label class="input-label">有效期（天）</label>
    <input type="number" class="input-field" id="lp-valid-days" value="7" min="1" max="90" style="width:80px;" />
  </div>

  <!-- 定位方式切换（复用现有 switchLoginScriptMode） -->
  <div class="form-group">
    <label class="input-label">定位方式</label>
    <div style="display:flex;gap:8px;">
      <button type="button" class="btn btn-secondary btn-sm" id="lp-mode-form-btn"
              onclick="switchLoginScriptMode('form')" style="background:var(--primary);color:#fff;">表单模式</button>
      <button type="button" class="btn btn-secondary btn-sm" id="lp-mode-custom-btn"
              onclick="switchLoginScriptMode('custom')">自定义脚本</button>
    </div>
  </div>

  <!-- 表单模式字段（复用现有 showLoginForm 的字段结构） -->
  <div id="lp-form-mode">
    <!-- 用户名选择器 + 类型 -->
    <!-- 密码选择器 + 类型 -->
    <!-- 提交按钮 + 类型 -->
    <!-- 成功标志 + 类型 -->
  </div>

  <!-- 自定义脚本字段（复用现有） -->
  <div id="lp-custom-mode" style="display:none;">
    <textarea id="lp-custom-script" class="input-field" style="width:100%;min-height:200px;font-family:Consolas,Monaco,monospace;font-size:12px;" placeholder="// Playwright 登录脚本"></textarea>
  </div>

  <!-- 创建后立即生成会话 -->
  <div class="form-group">
    <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:13px;">
      <input type="checkbox" id="lp-generate-now" checked />
      创建后立即生成会话（推荐）
    </label>
    <div style="font-size:11px;color:var(--ink-3);margin-top:4px;">
      勾选后，项目创建完成会自动用 Playwright 执行登录并保存会话快照，后续脚本生成和执行时直接复用
    </div>
  </div>
</div>
```

### 5.3 复用现有登录态配置组件

登录配置区的字段结构（用户名选择器、密码选择器、提交按钮、成功标志、自定义脚本）与现有 [showLoginForm](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html#L6585) 函数渲染的表单**完全一致**，可直接复用：

- `lp-username-selector` / `lp-username-selector-type`
- `lp-password-selector` / `lp-password-selector-type`
- `lp-submit-selector` / `lp-submit-selector-type`
- `lp-success-indicator` / `lp-success-indicator-type`
- `lp-custom-script`
- `switchLoginScriptMode()` 切换函数

为避免 ID 冲突，项目创建表单中的字段需加前缀（如 `pc-lp-username-selector`），或动态渲染时确保唯一性。

---

## 6. 多重防线实现汇总

### 防线1：项目创建表单强校验

| 项 | 内容 |
|----|------|
| 位置 | [handleCreateProject](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html#L2270) |
| 触发 | 用户点"创建项目"按钮 |
| 逻辑 | needsLogin=true 时，校验 loginUrl/username/password 非空 |
| 失败行为 | showToast 提示，阻止提交 |

### 防线3：脚本生成错误引导

| 项 | 内容 |
|----|------|
| 位置 | callGenerateScripts（新增函数） |
| 触发 | 调用 POST /generate 返回 400 |
| 逻辑 | 检测错误信息含"登录态"，弹 confirm 引导用户去配置 |
| 失败行为 | 中断脚本生成流程 |

### 防线4：用例确认预警

| 项 | 内容 |
|----|------|
| 位置 | handleConfirmTestCases（新增逻辑） |
| 触发 | 用户点"确认用例"进入脚本生成前 |
| 逻辑 | requiresLogin=1 且无会话时，confirm 提示 |
| 失败行为 | 用户可选"去配置"或"继续"（可跳过） |

### 防线5：执行禁止（既有）

| 项 | 内容 |
|----|------|
| 位置 | [handleExecuteTests L5465](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html#L5465) |
| 触发 | 用户点"执行选中用例" |
| 逻辑 | !confirmedLoginProfile 时阻止执行 |
| 失败行为 | showToast 提示"请先确认登录态" |

---

## 7. 实施步骤

| 步骤 | 改动位置 | 内容 |
|------|----------|------|
| 1 | HTML L1896 附近（测试浏览器后） | 新增"登录需求"单选 + 登录配置区 HTML |
| 2 | handleCreateProject 函数 | 新增 requiresLogin 收集、强校验、链式创建登录态+生成会话 |
| 3 | 新增 collectLoginConfig 函数 | 收集登录配置表单数据 |
| 4 | 新增 toggleLoginRequirement 函数 | 控制登录配置区展开/收起 |
| 5 | 脚本生成调用处 | 新增 project_id 参数；400 错误引导 |
| 6 | 用例确认函数 | 新增防线4预警逻辑 |
| 7 | 编辑项目表单 | 同步增加"登录需求"字段 |
| 8 | TestPilotAPI 对象 | 新增 getProject 方法，createProject 支持 requiresLogin |

---

## 8. 边界情况处理

| 场景 | 处理 |
|------|------|
| 用户选"无需登录"创建项目 | 跳过登录配置，项目 requiresLogin=0，后续不拦截 |
| 用户选"需要登录"但会话生成失败 | 项目创建成功，提示"会话生成失败，可稍后重试"，不阻塞项目创建 |
| 用户后续想改登录态 | 既有"登录态配置"管理面板保留，可随时增删改 |
| 测试登录功能的用例 | 用例级别标记 login_mode="anonymous"，执行时覆盖项目默认 |
| 编辑项目时切换"登录需求" | 切换为"无需登录"时不删除已有 profile，仅标记项目 requiresLogin=0；切换为"需要登录"时若已有 profile 则提示复用 |

---

## 9. 用户体验流程

### 9.1 典型流程（需要登录的项目）

```
用户点"新建项目"
  → 填写项目名称、应用 URL
  → 选择"需要登录"
  → 登录配置区展开，预填推荐选择器
  → 填写账号密码
  → 勾选"创建后立即生成会话"
  → 点"创建项目"
  → Loading: 创建项目中... → 创建登录态配置中... → 生成登录会话中...
  → 成功提示: "项目创建成功，登录会话已生成"
  → 跳转需求页面
```

### 9.2 典型流程（测试登录功能的项目）

```
用户点"新建项目"
  → 填写项目名称、应用 URL
  → 选择"无需登录"
  → 登录配置区不展开
  → 点"创建项目"
  → 成功提示: "项目创建成功"
  → 跳转需求页面
```

### 9.3 异常流程（漏配登录态）

```
用户选"需要登录"但会话生成失败
  → 项目已创建
  → 提示: "会话生成失败，可稍后在「登录态配置」中重试"
  → 用户继续走流程到用例确认
  → 防线4: confirm 提示"未生成会话，是否现在去配置？"
  → 用户坚持继续，进入脚本生成
  → 防线3: 后端返回 400，前端 confirm 提示去配置
  → 用户去配置登录态，重新生成脚本
```
