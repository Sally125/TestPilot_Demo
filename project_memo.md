# TestPilot 项目问题记录

## 概述

本文档记录了 TestPilot AI测试智能体项目在开发和调试过程中遇到的所有问题、根本原因及修复方案。

---

## 问题分类

### 一、函数定义与作用域问题

| 问题编号 | 问题描述 | 根本原因 | 修复方案 |
|---------|---------|---------|---------|
| F001 | `loadPageData is not defined` | 函数定义顺序问题，`switchPage` 在 `loadPageData` 定义前调用 | 将所有关键函数移至第一个script块开头 |
| F002 | 函数重复定义错误 | 多个script块中存在相同函数定义 | 删除原位置重复函数，统一在第一个script块中定义 |
| F003 | 渲染函数未找到 | `refreshProjectContent` 调用的渲染函数分散在不同script块 | 将 `renderRequirement` 等所有渲染函数集中移至第一个script块 |
| F004 | `switchPage` 函数缺失 | 页面多处调用但未定义 | 添加 `switchPage` 函数实现页面切换逻辑 |
| F005 | `projectData` 未初始化 | 全局变量未定义就被使用 | 添加 `initDefaultProjectData` 函数并在初始化时调用 |
| F006 | `SyntaxError: Unexpected token 'finally'` | `analyzeStream` 函数中括号和缩进错误，`finally` 块位置不正确 | 修正代码结构，确保 `finally` 块正确匹配 `try` 块 |
| F007 | `ReferenceError: confirmedLoginProfile is not defined` | 变量在第5218行定义，但在第3135行就已使用，多script块导致变量声明位置在使用位置之后 | 在文件开头统一声明全局变量，删除重复定义 |
| F008 | `TypeError: Cannot read properties of undefined (reading 'testcases')` | `projectList` 和 `projectData` 两个数组长度不一致，`projectList`有6个项目但`projectData`只有1个 | 移除`projectList`，统一使用`projectData`作为唯一数据源 |
| F009 | 首页显示硬编码的预制数据（电商平台、出行App等） | 首页项目卡片、活动记录、待处理任务均为硬编码的示例数据，与真实数据无关 | 将首页内容改为动态生成，从`projectData`读取真实数据 |

**修复文件**: [AI测试智能体_TestPilot.html](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html)

---

### 二、数据持久化问题

| 问题编号 | 问题描述 | 根本原因 | 修复方案 |
|---------|---------|---------|---------|
| D001 | 历史生成的需求、用例、执行、报告刷新后消失 | 初始化时只加载项目基本信息，未加载关联数据 | 添加 `loadProjectFullData` 函数，初始化时加载完整数据 |
| D002 | 测试用例数与稳定性页面不一致 | 测试用例页面显示前端内存数据，稳定性检查从数据库获取所有用例 | 稳定性检查完成后强制同步测试用例数据 |

**修复文件**: [AI测试智能体_TestPilot.html](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html)

---

### 三、AI服务性能问题

| 问题编号 | 问题描述 | 根本原因 | 修复方案 |
|---------|---------|---------|---------|
| P001 | AI解析需求速度慢 | AI模型本身处理耗时（15-45秒），无进度反馈 | 后端添加SSE流式响应，前端实时显示进度 |
| P002 | 重试策略过于保守 | 5次重试，每次间隔3秒，失败时最多额外等待12秒 | 重试次数减至3次，间隔减至2秒 |

**修复文件**: [services.py](file:///e:/hkx_project/TestPilot/testpilot-backend/app/services.py)、[routes.py](file:///e:/hkx_project/TestPilot/testpilot-backend/app/routes.py)、[AI测试智能体_TestPilot.html](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html)

---

### 四、API调用错误

| 问题编号 | 问题描述 | 根本原因 | 修复方案 |
|---------|---------|---------|---------|
| A001 | `body.requirement_text: String should have at least 10 characters` | 后端验证要求至少10字符，前端仅检查非空 | 前端添加长度验证（<10字符时阻止请求） |
| A002 | `net::ERR_ABORTED http://localhost:8000/api/analyze/stream` | 流式请求缺少超时控制和请求取消机制 | 添加 `AbortController`、5分钟超时、`keepalive: true` |

**修复文件**: [AI测试智能体_TestPilot.html](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html)

---

### 五、业务逻辑问题

| 问题编号 | 问题描述 | 根本原因 | 修复方案 |
|---------|---------|---------|---------|
| B001 | AI分析页面有初始值（虚假数据） | `initDefaultProjectData` 包含大量优惠券系统的示例数据 | 清空默认项目数据，只保留空的示例项目 |
| B002 | 生成的用例数少于功能点数 | `generate_scripts` 方法虽有检查但验证失败后仍返回cases，未抛出异常 | 添加 `raise ValueError` 确保验证失败时中断流程 |
| B003 | AI需求分析页面初始显示"AI正在解析" | `renderAnalysis` 函数判断逻辑错误，features为空时直接显示分析中状态 | 修改逻辑：无需求文本显示引导，有需求无分析结果才显示分析中 |
| B004 | 稳定性检查选择器稳定性标绿 | 选择器检查仅判断 `passed` 字段，未考虑风险数与修复数是否匹配 | 修改判断逻辑：只有风险数等于修复数时才标绿 |

**修复文件**: [AI测试智能体_TestPilot.html](file:///e:/hkx_project/TestPilot/AI测试智能体_TestPilot.html)、[services.py](file:///e:/hkx_project/TestPilot/testpilot-backend/app/services.py)、[routes.py](file:///e:/hkx_project/TestPilot/testpilot-backend/app/routes.py)

---

## 修复总结

### 前端修复（AI测试智能体_TestPilot.html）
1. 函数集中管理：所有关键函数统一移至第一个script块
2. 数据初始化：`initDefaultProjectData` 清空示例数据
3. 数据同步：`loadProjectFullData` 加载完整项目数据
4. 输入验证：需求文本长度校验（≥10字符）
5. 流式API：`analyzeStream` 添加超时控制和进度回调
6. 数据一致性：稳定性检查后同步测试用例
7. 代码结构：修复 `analyzeStream` 函数中 `try-finally` 结构错误
8. 变量声明：全局变量统一在文件开头声明，避免重复定义
9. 页面逻辑：修复 `renderAnalysis` 初始显示状态错误，区分无需求/有需求未分析/分析完成三种状态

### 后端修复（testpilot-backend）
1. 流式响应：`chat_stream` 方法 + `/analyze/stream` 接口
2. 用例约束：`generate_scripts` 强制用例数 ≥ 功能点数
3. 重试优化：重试次数3次，间隔2秒

---

## 关键教训

1. **函数定义顺序**：JavaScript中函数必须在调用前定义，多script块会导致作用域问题
2. **数据一致性**：前端内存数据与后端数据库数据必须同步，否则会出现显示不一致
3. **用户体验**：长时间操作（如AI分析）必须提供进度反馈，否则用户会感觉卡顿
4. **输入验证**：前端验证应与后端验证规则保持一致，避免不必要的API调用
5. **资源管理**：流式请求和长连接需要超时控制和资源清理机制
