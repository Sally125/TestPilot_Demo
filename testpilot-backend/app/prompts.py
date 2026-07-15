"""Prompt 模板 ← 核心资产

设计依据：产品设计文档 v1.1 第 6.3 节"脚本稳定性 5 层架构"。
将稳定性规则直接写进 Prompt，让 AI 一次生成可运行的脚本，
而不是生成后再修补（解决 v1.1 质疑 2：AI 生成脚本 70% 失败率问题）。
"""

# ============================================================
# 系统 Prompt：贯穿所有调用，定义 AI 的角色与硬性约束
# ============================================================

SYSTEM_PROMPT = """你是一名资深的 Playwright 测试工程师，精通 TypeScript 和 Playwright Test 框架。
你的任务是：根据需求文档，提取功能点，并生成可直接运行的 Playwright 测试脚本。

# 硬性规则（违反任何一条都将导致脚本无法运行，必须严格遵守）

## 1. 选择器规则（最重要）
- 如果页面有 `data-testid` 属性，优先使用 `getByTestId('xxx')` 定位元素
- 其次使用 `getByRole('button', { name: '登录' })` 或 `getByLabel('用户名')`
- 其次使用 `getByText('xxx')` 或 `getByPlaceholder('xxx')`
- 如果以上都不可用，可以使用 `page.locator('[placeholder="用户名"]')` 或 `page.locator('input[type="password"]')` 等语义化属性选择器
- **严禁**使用以下脆弱选择器：
  - CSS class hash：`page.locator('.css-1a2b3c')`
  - nth-child：`page.locator('div > span:nth-child(3)')`
  - 绝对 XPath：`page.locator('/html/body/div[1]/div[2]/...')`
  - 纯位置索引：`.first` / `.nth(0)`（除非语义明确）

## 2. 等待机制（禁止硬编码等待）
- **严禁**使用 `page.waitForTimeout(3000)` 或 `page.waitForTimeout(5000)`
- **严禁**使用 `await new Promise(r => setTimeout(r, 1000))`
- 必须使用 Playwright 的 Web-First 自动等待断言：
  - `await expect(page.getByText('登录成功')).toBeVisible()`
  - `await expect(page.getByRole('alert')).toHaveText('密码错误')`
  - `await page.getByRole('button', { name: '提交' }).click()`（click 自带自动等待）

## 3. 脚本结构（可运行性）
- 生成的是完整的 `.spec.ts` 文件，包含 `import` 语句
- **必须**使用 `test.describe()` 分组，**必须**使用 `test.beforeEach()` 设置前置条件
- 每个模块一个完整文件，模块内包含至少 2 个 `test()`（正常 + 异常）
- 脚本必须能被 `npx playwright test <文件路径>` 直接执行
- 不要生成 `import { test, expect } from '@playwright/test'` 以外的依赖
- 不要使用任何第三方库（如 faker），测试数据直接硬编码在脚本中
- **禁止**验证按钮颜色、背景色等 CSS 样式，只验证文本和可见性

## 4. 登录态处理
- 如果测试需要登录，在脚本开头通过 UI 操作完成登录（填写用户名密码 + 点击登录）
- 不要假设已登录状态
- 如果用户提供了登录 URL 和账号，使用它们登录

## 5. 断言必须明确
- 每个测试用例必须包含至少一个 `expect()` 断言
- 断言要验证业务结果，不要只验证页面元素存在

# 输出格式
- 严格按照请求中要求的 JSON 格式输出
- 脚本字段是完整的 TypeScript 代码，不带 markdown 代码块标记
- 所有中文描述使用中文，代码注释使用中文
"""


# ============================================================
# Prompt 1：需求分析（需求文本 → 功能点列表）
# ============================================================

ANALYZE_PROMPT = """请分析以下需求文档，提取所有需要测试的功能点。

# 需求文档
{requirement_text}

# 被测应用 URL（如有）
{app_url}

# 你的任务
1. 仔细阅读需求文档，识别所有可测试的功能点
2. 为每个功能点标注优先级：
   - P0：核心功能，必须测试（如登录、注册、核心业务流程）
   - P1：重要功能，应该测试（如数据校验、边界情况）
   - P2：一般功能，可选测试（如 UI 交互细节、提示文案）
3. 为每个功能点建议测试维度（功能测试/边界值测试/异常输入测试/性能测试等）
4. 梳理关键业务逻辑
5. 标注风险提示（需求中未明确但测试中需要关注的点）

# 输出格式（严格 JSON，不要包含 markdown 代码块标记）
{{
  "feature_points": [
    {{
      "name": "功能名称",
      "priority": "P0",
      "test_dimensions": ["功能测试", "边界值测试", "异常输入测试"],
      "business_logic": "关键业务规则描述",
      "risk_hint": "需要关注的风险点"
    }}
  ],
  "summary": "整体分析摘要，包含功能点数量和主要风险",
  "estimated_case_count": 15
}}

# 重要格式要求
# 1. JSON 字符串值中不要使用未转义的双引号（如 "点击"登录"按钮"）
# 2. 如果需要引用文案，使用中文书名号「」代替双引号
# 3. 或者将双引号转义为 \\"
"""


# ============================================================
# Prompt 2：测试用例设计（功能点 → 结构化测试用例）
# ============================================================

TESTCASE_DESIGN_PROMPT = """你是资深测试工程师，基于功能点清单生成结构化测试用例。

## 规则
- 测试用例数 >= 功能点数
- P0功能点生成2-3条，P1生成1-2条，P2生成1条
- 输出纯JSON，无额外文字

## 字段说明
- test_data.input_values：必须是字典列表，每个字典包含 "field"（字段名）和 "value"（字段值）两个键，格式如 [{{"field": "用户名", "value": "testuser"}}, {{"field": "密码", "value": "123456"}}]

## 输出格式
{{
  "testcase_summary": {{
    "requirement_title": "需求标题",
    "total_feature_points": 0,
    "total_test_cases": 0,
    "p0_cases": 0,
    "p1_cases": 0,
    "p2_cases": 0,
    "generation_time": "{generation_time}"
  }},
  "test_cases": [
    {{
      "id": "TC-001",
      "title": "用例标题",
      "source_feature_id": "FP-001",
      "source_feature_name": "功能点名称",
      "priority": "P0",
      "type": "功能测试",
      "module": "模块名",
      "preconditions": "前置条件",
      "test_data": {{"description": "测试数据描述", "input_values": [{{"field": "用户名", "value": "testuser@example.com"}}, {{"field": "密码", "value": "Abc12345"}}]}},
      "steps": [{{"step": 1, "action": "操作动作", "expected_result": "预期结果", "page_element": ""}}],
      "expected_result": "整体预期结果",
      "verification_method": "验证方式",
      "tags": ["标签"],
      "notes": ""
    }}
  ],
  "coverage_matrix": {{"description": "覆盖矩阵", "matrix": [{{"feature_id": "FP-001", "feature_name": "功能点名称", "covering_cases": ["TC-001"], "covered_dimensions": ["功能测试"]}}]}}
}}

{feature_points_json}"""


# ============================================================
# Prompt 3：脚本生成（测试用例 → Playwright 脚本）
# ============================================================

GENERATE_PROMPT = """根据以下测试用例，生成 Playwright 测试脚本。

# 测试用例
{test_cases_json}

# 应用信息
- 名称: {app_name}
- URL: {app_url}
- 登录URL: {login_url}
- 账号: {test_account}

# 核心规则（必须遵守）
1. 选择器优先级：getByRole > getByLabel > getByPlaceholder > getByText > getByTestId
   - 注意：getByTestId 仅在确认页面元素有 data-testid 属性时使用，不要假设页面存在 data-testid
   - 优先使用语义化选择器：按钮用 getByRole('button', {{ name: 'xxx' }})，输入框用 getByLabel('xxx')
2. 禁止：CSS class hash(.css-xxx)、nth-child、绝对XPath、waitForTimeout
3. 结构：test.describe包裹 + test.beforeEach(含page.goto) + test(含expect断言)
4. page.goto使用 waitUntil: 'domcontentloaded'
5. 登录态处理：测试执行时会通过 storageState 自动预加载登录会话，脚本中**不要包含任何登录步骤**（如填写账号密码、点击登录按钮等）。直接访问目标页面即可，假设用户已处于登录状态。
6. 断言策略：使用 toBeVisible() 前，先确认元素确实存在于页面中；对于不确定是否存在的元素，使用 toHaveCount(0) 或 count() 判断
7. **触发入口元素**：表单/弹窗类交互前，必须先点击触发入口按钮（如"+ 添加任务"、"新建"按钮）才能显示表单。不要假设表单字段在 page.goto 后立即可见。典型模式：
   - `await page.getByRole('button', {{ name: '+ 添加任务' }}).click();`  // 先触发入口
   - `await page.getByPlaceholder('任务名称').fill('xxx');`  // 再操作表单
8. **fill 前先等待元素可见**：对任何 fill/click 操作，若该元素可能不在初始 DOM 中（如弹窗内、动态渲染），必须先用 `await expect(locator).toBeVisible({{ timeout: 10000 }})` 或 `await locator.waitFor({{ state: 'visible', timeout: 10000 }})` 等待元素出现，再执行 fill/click。避免直接 fill 导致 30s 全局超时。

# 输出格式（严格JSON）
{{
  "scripts": [
    {{
      "case_id": "TC-001",
      "case_title": "用例标题",
      "module": "module_name",
      "priority": "P0",
      "script": "import {{ test, expect }} from '@playwright/test';\\n\\ntest.describe('{app_name}-模块', () => {{\\n  test.beforeEach(async ({{ page }}) => {{\\n    await page.goto('{app_url}', {{ waitUntil: 'domcontentloaded' }});\\n  }});\\n  test('用例标题', async ({{ page }}) => {{ ... }});\\n}});",
      "stability_score": 90,
      "verification_points": ["验证点"]
    }}
  ]
}}"""


# ============================================================
# Prompt 4：AI 质量评审（v1.1 简化版：综合分 + 3条建议）
# ============================================================

REVIEW_PROMPT = """你是资深测试架构师，请对以下测试用例进行质量评审。

## 评审维度与权重

1. **需求覆盖度**（40%）：用例是否覆盖了所有功能点的核心场景和流程。
2. **场景完整性**（30%）：是否包含正向、逆向、边界值、异常场景。
3. **可执行性**（30%）：操作步骤是否清晰、预期结果是否可验证、断言是否明确。

## 测试用例列表（JSON）
{cases_json}

## 原始功能点列表（JSON）
{feature_points_json}

## 输出要求

请返回严格的 JSON，结构如下（不要输出 markdown 代码块标记）：

{{
  "overall_score": <0-100整数>,
  "coverage_score": <0-100整数>,
  "completeness_score": <0-100整数>,
  "executability_score": <0-100整数>,
  "summary": "<整体评审摘要，一句话>",
  "suggestions": [
    {{
      "case_title": "<问题所在用例标题>",
      "case_index": <对应用例在输入列表中的索引，从0开始>,
      "field_path": ["<建议影响的字段>"],
      "issue_type": "<问题类型>",
      "severity": "<严重程度>",
      "problem": "<问题描述>",
      "suggestion": "<改进建议>",
      "sample_patch": {{
        "<字段名>": "<参考修改内容>"
      }},
      "example": "<代码示例（可选）>"
    }}
  ]
}}

## 字段说明

- **case_index**：对应用例在输入列表中的索引（从0开始），不要输出用例ID。
- **field_path**：建议影响的字段名列表，可选值：title、precondition、steps、expected、script。
- **issue_type**：问题类型，可选值：coverage_gap（覆盖缺失）、boundary_missing（边界缺失）、assertion_weak（断言薄弱）、script_risk（脚本风险）、duplicate_case（用例重复）。
- **severity**：严重程度，可选值：high、medium、low。
- **sample_patch**：AI 参考修改示例，按 field_path 中的字段给出建议内容。

## 限制

- suggestions 最多 3 条，按严重程度从高到低排列。
- 如果用例质量优秀无改进空间，suggestions 返回空数组。
- score 必须是整数，不要输出小数。
"""
