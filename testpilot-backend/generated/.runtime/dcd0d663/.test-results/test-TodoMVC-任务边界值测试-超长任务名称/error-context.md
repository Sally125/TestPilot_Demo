# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-任务边界值测试 >> 超长任务名称
- Location: testpilot-backend\generated\.runtime\dcd0d663\test.spec.ts:8:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByPlaceholder('任务名称')

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
        - link "📝 复盘记录" [ref=e24] [cursor=pointer]:
          - /url: /dashboard/wrong-questions
          - generic [ref=e25]: 📝
          - generic [ref=e26]: 复盘记录
        - link "📰 申论文章" [ref=e27] [cursor=pointer]:
          - /url: /dashboard/articles
          - generic [ref=e28]: 📰
          - generic [ref=e29]: 申论文章
        - link "📇 每日背诵" [ref=e30] [cursor=pointer]:
          - /url: /dashboard/daily-cards
          - generic [ref=e31]: 📇
          - generic [ref=e32]: 每日背诵
        - link "✨ 素材本" [ref=e33] [cursor=pointer]:
          - /url: /dashboard/materials
          - generic [ref=e34]: ✨
          - generic [ref=e35]: 素材本
        - link "📅 学习计划" [ref=e36] [cursor=pointer]:
          - /url: /dashboard/plans
          - generic [ref=e37]: 📅
          - generic [ref=e38]: 学习计划
        - link "📊 数据统计" [ref=e39] [cursor=pointer]:
          - /url: /dashboard/stats
          - generic [ref=e40]: 📊
          - generic [ref=e41]: 数据统计
        - link "⚙️ 个人设置" [ref=e42] [cursor=pointer]:
          - /url: /dashboard/settings
          - generic [ref=e43]: ⚙️
          - generic [ref=e44]: 个人设置
      - generic [ref=e46]:
        - generic [ref=e47]: 测
        - paragraph [ref=e49]: 测试员
        - button "退出" [ref=e50] [cursor=pointer]
    - main [ref=e51]:
      - generic [ref=e53]:
        - generic [ref=e54]:
          - heading "智能Todo" [level=1] [ref=e55]
          - button "+ 添加任务" [ref=e56] [cursor=pointer]
        - generic [ref=e57]:
          - heading "待办 (0)" [level=3] [ref=e59]:
            - text: 待办
            - generic [ref=e60]: (0)
          - heading "进行中 (0)" [level=3] [ref=e62]:
            - text: 进行中
            - generic [ref=e63]: (0)
          - heading "已完成 (0)" [level=3] [ref=e65]:
            - text: 已完成
            - generic [ref=e66]: (0)
  - alert [ref=e67]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-任务边界值测试', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('http://localhost:3001/dashboard/tasks', { waitUntil: 'domcontentloaded' });
  6  |   });
  7  | 
  8  |   test('超长任务名称', async ({ page }) => {
  9  |     const longName = 'a'.repeat(51);
> 10 |     await page.getByPlaceholder('任务名称').fill(longName);
     |                                         ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  11 |     await page.getByPlaceholder('描述').fill('边界测试');
  12 |     await page.getByRole('button', { name: '提交' }).click();
  13 |     // 预期：要么成功创建（名称可能被截断或完整显示），要么提示错误
  14 |     await expect(page.getByText(longName).or(page.getByText('名称过长'))).toBeVisible();
  15 |   });
  16 | 
  17 |   test('特殊字符任务名称', async ({ page }) => {
  18 |     const specialName = '<script>alert("xss")</script>';
  19 |     await page.getByPlaceholder('任务名称').fill(specialName);
  20 |     await page.getByRole('button', { name: '提交' }).click();
  21 |     // 验证：任务创建或显示经过转义的内容
  22 |     await expect(page.getByText('script')).toBeVisible();
  23 |   });
  24 | });
```