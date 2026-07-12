# Day 1 Prompt 调优记录与模板

> 被测应用：考公大师（`http://localhost:3000/login`）
> 代码位置：`app/prompts.py`
> 最后更新：2026-07-11

---

## 一、Day 1 目标与偏差

| 原计划 | 实际执行 | 原因 |
|--------|----------|------|
| 电商平台用户登录 | 考公大师用户登录 | 无可用的电商平台被测应用 |
| 一文件一 `test()` | 按模块分组，`test.describe` + 多个 `test()` | 结构更清晰，便于批量执行 |
| 只跑第一条用例 | 批量执行所有模块 + `report.json` | 完整验收闭环 |

---

## 二、Prompt 版本迭代

### v1 — 初始版（问题多）

**特征**
- 每个功能点生成独立 `.spec.ts`，单 `test()` 函数
- `test.describe` 仅写在模板示例中，AI 实际不遵循

**问题**
| 问题 | 表现 |
|------|------|
| 结构松散 | generated 目录 `test.describe` 匹配数为 0 |
| 一用例一文件 | 10 个功能点 → 10 个文件，难以维护 |
| 选择器偶尔脆弱 | 个别脚本使用 `locator('body')` |
| 错误文案硬编码 | `getByText('请输入邮箱')` 与实际页面不符 |

**通过率**：单条简单用例（页面标题）可跑通，复杂用例不稳定

---

### v2 — 结构强化版

**改动**
- `GENERATE_PROMPT` 强制 `test.describe` + `test.beforeEach` + 至少 2 个 `test()`
- 按模块输出 2-3 个 `.spec.ts`（`page_elements` / `form_validation` / `login_navigation`）
- 写入考公大师元素锚点表
- 表单错误断言改为正则：`/邮箱|必填/`
- 禁止颜色/背景色断言
- `services.py` 增加 `_validate_script()`，不合格自动重试（最多 3 次）
- `run_demo.py` 改为按模块保存 + 批量执行 + `report.json`

**结构校验规则**
```
必须含 test.describe
必须含 test.beforeEach
至少 2 个 test(
必须含 expect(
禁止 waitForTimeout / .css- / nth-child
```

**结果**：脚本结构 100% 合格，但执行仍失败（见 v2.1）

---

### v2.1 — 页面加载修复版（当前生效版）

**问题**：`page.goto` 默认等待 `load` 事件，考公大师页面 30s 内无法完成 `load`

```
page.goto: Test timeout of 30000ms exceeded.
waiting until "load"
```

> 注：HTTP 请求 7s 内返回 200，但 `load` 事件因长连接/资源未触发。

**修复**：`page.goto` 统一改为 `waitUntil: 'domcontentloaded'`

```typescript
await page.goto('http://localhost:3000/login', { waitUntil: 'domcontentloaded' });
```

**修复后验证**（`page_elements.spec.ts`，5 条用例）：

| 用例 | 结果 |
|------|------|
| 页面标题显示欢迎回来 | 通过 |
| 邮箱输入框 placeholder | 通过 |
| 密码输入框 type=password | 通过 |
| 登录按钮可点击 | 通过 |
| 注册链接文本可见 | **失败** — 页面文案与需求不一致 |

**通过率**：4/5（80%）

---

## 三、调优踩坑清单

| # | 踩坑 | 根因 | 修复方式 |
|---|------|------|----------|
| 1 | `npx` 找不到 | Windows 下 `subprocess` 无法直接调用 `npx.CMD` | `shutil.which('npx')` 获取完整路径 |
| 2 | `No tests found` | 在系统临时目录执行，无 `node_modules` | `cwd` 设为项目根目录，脚本写项目内 |
| 3 | 被测应用超时 | 应用未启动 | 执行前确认 `localhost:3000` 可访问 |
| 4 | `page.goto` 超时 | 等待 `load` 事件 | 改用 `waitUntil: 'domcontentloaded'` |
| 5 | 测试账号未生效 | `.env` 未保存到磁盘 | 填写后 Ctrl+S 保存 |
| 6 | API 连接失败 | 系统代理干扰 | 设置 `NO_PROXY=*` |
| 7 | 注册链接断言失败 | 需求文案 ≠ 实际页面文案 | 用宽松匹配或先确认实际 DOM |

---

## 四、考公大师页面元素对照表

| 元素 | 定位方式 | 验证状态 | 备注 |
|------|----------|----------|------|
| 页面标题 | `getByText('欢迎回来')` | 已验证 | |
| 邮箱输入框 | `getByLabel('邮箱')` | 已验证 | placeholder: `your@email.com` |
| 密码输入框 | `getByLabel('密码')` | 已验证 | type=password |
| 登录按钮 | `getByRole('button', { name: '登录' })` | 已验证 | 不验证颜色 |
| 注册链接 | `getByText('还没有账号？立即注册')` | **未通过** | 实际页面文案可能不同，需确认 |

---

## 五、批量执行记录

### 运行 1 — `20260711_225455`（应用未启动）

- 结构校验：3/3 通过
- 执行：0/3 通过
- 原因：`localhost:3000` 不可访问

### 运行 2 — `20260711_231224`（应用已启动，goto 未修复）

- 结构校验：3/3 通过
- 执行：0/3 通过
- 原因：`page.goto` 等待 `load` 超时

### 运行 3 — `20260711_231224`（goto 修复后，手动验证）

- `page_elements.spec.ts`：4/5 通过（80%）
- 唯一失败：注册链接文案不匹配

---

## 六、Prompt 模板（可直接复用）

以下为 Day 1 调优后的标准模板结构。换项目时替换 `{占位符}` 即可。

### 6.1 SYSTEM_PROMPT 模板

```
角色：资深 Playwright 测试工程师

硬性规则：
1. 选择器：getByTestId > getByRole > getByLabel > getByText，禁止 CSS hash / nth-child / XPath
2. 等待：禁止 waitForTimeout，使用 expect().toBeVisible() 等 Web-First 断言
3. 结构：必须 test.describe + test.beforeEach + 至少 2 个 test()
4. 页面加载：page.goto 必须使用 { waitUntil: 'domcontentloaded' }
5. 断言：每个 test 至少一个 expect()，验证业务结果
6. 禁止：颜色/背景色断言、第三方库、硬编码等待
```

### 6.2 ANALYZE_PROMPT 模板

```
输入：
  - 需求文档：{requirement_text}
  - 被测应用 URL：{app_url}

任务：
  1. 提取可测试功能点
  2. 标注优先级 P0/P1/P2
  3. 建议测试维度（功能/边界/异常）
  4. 标注风险提示

输出 JSON：
{
  "feature_points": [{
    "name": "功能名称",
    "priority": "P0",
    "test_dimensions": ["功能测试", "边界值测试"],
    "business_logic": "业务规则",
    "risk_hint": "风险点"
  }],
  "summary": "摘要",
  "estimated_case_count": 12
}
```

### 6.3 GENERATE_PROMPT 模板

```
输入：
  - 功能点列表：{feature_points_json}
  - 应用 URL：{app_url}
  - 登录 URL：{login_url}
  - 测试账号：{test_account}

【元素锚点表】← 换项目时替换此表
| 元素     | 定位方式                              |
|----------|---------------------------------------|
| 页面标题 | page.getByText('欢迎回来')            |
| 邮箱     | page.getByLabel('邮箱')               |
| 密码     | page.getByLabel('密码')               |
| 登录按钮 | page.getByRole('button', { name: '登录' }) |

【结构硬性约束】
1. 按模块分组，每模块 1 个 .spec.ts
2. 必须 test.describe + test.beforeEach + >= 2 个 test()
3. beforeEach 中 page.goto 使用 waitUntil: 'domcontentloaded'
4. 禁止每个 test 内重复 goto
5. 表单错误用正则：/邮箱|必填/
6. 禁止颜色断言

【脚本模板】
import { test, expect } from '@playwright/test';

test.describe('{应用名}-{模块名}', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('{login_url}', { waitUntil: 'domcontentloaded' });
  });

  test('{正常流程标题}', async ({ page }) => {
    // 操作 + expect 断言
  });

  test('{异常流程标题}', async ({ page }) => {
    // 操作 + expect 断言
  });
});

【输出 JSON】
{
  "cases": [{
    "title": "考公大师-表单验证",
    "module": "form_validation",
    "priority": "P0",
    "precondition": "用户未登录，浏览器打开登录页",
    "steps": ["步骤1", "步骤2"],
    "expected": "预期结果",
    "script": "完整 .spec.ts 代码（\\n 换行）",
    "stability_score": 90
  }]
}

注意：输出 2-3 个 cases（每模块一个），不要每 test 一个 case
```

### 6.4 脚本结构校验模板（`services.py`）

换项目时可调整校验项：

```python
def _validate_script(script: str) -> list[str]:
    errors = []
    if "test.describe" not in script:     errors.append("缺少 test.describe")
    if "test.beforeEach" not in script:   errors.append("缺少 test.beforeEach")
    if script.count("test(") < 2:         errors.append("至少需要 2 个 test()")
    if "expect(" not in script:          errors.append("缺少 expect() 断言")
    if "domcontentloaded" not in script:  errors.append("page.goto 未使用 domcontentloaded")
    if "waitForTimeout" in script:        errors.append("禁止使用 waitForTimeout")
    return errors
```

---

## 七、环境配置模板

```env
# .env 必填项
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.xxx.com
DEEPSEEK_MODEL=deepseek-v4-flash

TARGET_APP_URL=http://localhost:3000
LOGIN_URL=http://localhost:3000/login
TEST_USERNAME=测试邮箱
TEST_PASSWORD=测试密码
BROWSER_TIMEOUT=30000
```

---

## 八、执行命令模板

```powershell
# 1. 确认被测应用可访问
Invoke-WebRequest http://localhost:3000/login -TimeoutSec 10

# 2. 跑完整链路
cd testpilot-backend
$env:Path = "E:\Ai_Test;" + $env:Path
$env:NO_PROXY = "*"
python run_demo.py

# 3. 单独跑某个模块
cd ..   # 项目根目录（含 node_modules）
npx playwright test testpilot-backend/generated/{timestamp}/page_elements.spec.ts
```

---

## 九、换项目 Checklist

接入新项目时，按此清单逐项替换：

- [ ] 更新 `DEMO_REQUIREMENT` 需求文本
- [ ] 更新 `GENERATE_PROMPT` 中的**元素锚点表**
- [ ] 更新 `.env` 中的 URL 和测试账号
- [ ] 确认 `page.goto` 使用 `domcontentloaded`（如仍超时，尝试 `commit`）
- [ ] 用 1 条简单用例验证选择器（如页面标题）
- [ ] 跑 `run_demo.py` 查看 `report.json` 通过率
- [ ] 根据失败用例回调 Prompt 中的断言文案

---

## 十、Day 2 待办

- [ ] 确认注册链接实际文案，更新元素锚点表
- [ ] HTTP 接口冒烟测试（`scripts/smoke_api.py`）
- [ ] 前端对接 `/api/analyze` 和 `/api/generate`
- [ ] 增加 `playwright.config.ts` 统一超时和 `navigationTimeout`
