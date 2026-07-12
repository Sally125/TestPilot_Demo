# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-任务添加功能测试 >> 添加任务名称为空
- Location: testpilot-backend\generated\.runtime\c75069b3\test.spec.ts:16:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByPlaceholder('描述')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - complementary [ref=e3]:
      - link "🎯 考公大师" [ref=e5] [cursor=pointer]:
        - /url: /dashboard
        - generic [ref=e6]: 🎯
        - generic [ref=e7]: 考公大师
      - navigation [ref=e8]:
        - link "🏠 首页" [ref=e9] [cursor=pointer]:
          - /url: /dashboard
          - generic [ref=e10]: 🏠
          - generic [ref=e11]: 首页
        - link "📋 考试管理" [ref=e12] [cursor=pointer]:
          - /url: /dashboard/exams
          - generic [ref=e13]: 📋
          - generic [ref=e14]: 考试管理
        - link "✅ 智能Todo" [ref=e15] [cursor=pointer]:
          - /url: /dashboard/tasks
          - generic [ref=e16]: ✅
          - generic [ref=e17]: 智能Todo
        - link "📖 易错成语" [ref=e18] [cursor=pointer]:
          - /url: /dashboard/idioms
          - generic [ref=e19]: 📖
          - generic [ref=e20]: 易错成语
        - link "🔄 每日复习" [ref=e21] [cursor=pointer]:
          - /url: /dashboard/review
          - generic [ref=e22]: 🔄
          - generic [ref=e23]: 每日复习
        - link "学习计划" [ref=e24] [cursor=pointer]:
          - /url: /dashboard/plans
          - generic [ref=e25]: 学习计划
        - link "复盘记录" [ref=e26] [cursor=pointer]:
          - /url: /dashboard/reviews
          - generic [ref=e27]: 复盘记录
        - link "📊 数据统计" [ref=e28] [cursor=pointer]:
          - /url: /dashboard/stats
          - generic [ref=e29]: 📊
          - generic [ref=e30]: 数据统计
        - link "⚙️ 个人设置" [ref=e31] [cursor=pointer]:
          - /url: /dashboard/settings
          - generic [ref=e32]: ⚙️
          - generic [ref=e33]: 个人设置
      - generic [ref=e35]:
        - generic [ref=e36]: U
        - paragraph [ref=e38]: 用户
        - button "退出" [ref=e39] [cursor=pointer]
    - main [ref=e40]:
      - generic [ref=e42]:
        - generic [ref=e43]:
          - heading "智能Todo" [level=1] [ref=e44]
          - button "+ 添加任务" [ref=e45] [cursor=pointer]
        - generic [ref=e46]:
          - heading "待办 (0)" [level=3] [ref=e48]:
            - text: 待办
            - generic [ref=e49]: (0)
          - heading "进行中 (0)" [level=3] [ref=e51]:
            - text: 进行中
            - generic [ref=e52]: (0)
          - heading "已完成 (0)" [level=3] [ref=e54]:
            - text: 已完成
            - generic [ref=e55]: (0)
  - alert [ref=e56]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-任务添加功能测试', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('http://localhost:3001/dashboard/tasks', { waitUntil: 'domcontentloaded' });
  6  |   });
  7  | 
  8  |   test('正常添加任务', async ({ page }) => {
  9  |     await page.getByPlaceholder('任务名称').fill('测试任务');
  10 |     await page.getByPlaceholder('描述').fill('这是一个测试任务');
  11 |     await page.getByLabel('截止日期').fill('2025-12-31');
  12 |     await page.getByRole('button', { name: '提交' }).click();
  13 |     await expect(page.getByText('测试任务')).toBeVisible();
  14 |   });
  15 | 
  16 |   test('添加任务名称为空', async ({ page }) => {
> 17 |     await page.getByPlaceholder('描述').fill('测试描述');
     |                                       ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  18 |     await page.getByRole('button', { name: '提交' }).click();
  19 |     await expect(page.getByText('任务名称不能为空')).toBeVisible();
  20 |   });
  21 | });
```