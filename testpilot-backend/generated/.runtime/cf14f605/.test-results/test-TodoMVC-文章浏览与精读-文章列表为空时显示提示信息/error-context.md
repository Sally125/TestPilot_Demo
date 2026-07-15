# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-文章浏览与精读 >> 文章列表为空时显示提示信息
- Location: testpilot-backend\generated\.runtime\cf14f605\test.spec.ts:16:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('暂无推送文章')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText('暂无推送文章')

```

```yaml
- complementary:
  - link "🎯 考公大师":
    - /url: /dashboard
  - navigation:
    - link "🏠 首页":
      - /url: /dashboard
    - link "📋 考试管理":
      - /url: /dashboard/exams
    - link "✅ 智能Todo":
      - /url: /dashboard/tasks
    - link "📖 易错成语":
      - /url: /dashboard/idioms
    - link "🔄 每日复习":
      - /url: /dashboard/review
    - link "📝 复盘记录":
      - /url: /dashboard/wrong-questions
    - link "📰 申论文章":
      - /url: /dashboard/articles
    - link "📇 每日背诵":
      - /url: /dashboard/daily-cards
    - link "✨ 素材本":
      - /url: /dashboard/materials
    - link "📅 学习计划":
      - /url: /dashboard/plans
    - link "📊 数据统计":
      - /url: /dashboard/stats
    - link "⚙️ 个人设置":
      - /url: /dashboard/settings
  - text: 测
  - paragraph: 测试员
  - button "退出"
- main:
  - heading "你好，测试员 👋" [level=1]
  - paragraph: 今天也要加油备考哦！
  - heading "本周专注统计" [level=2]
  - text: 📊
  - paragraph: 本周还没有完成的任务，开始学习吧！
  - text: 📅
  - heading "学习计划" [level=3]
  - paragraph: 制定并管理你的学习计划
  - link "前往 →":
    - /url: /dashboard/plans
  - text: 📝
  - heading "复盘记录" [level=3]
  - paragraph: 记录每日学习心得与总结
  - link "前往 →":
    - /url: /dashboard/reviews
  - text: 📊
  - heading "数据统计" [level=3]
  - paragraph: 可视化你的备考数据
  - link "前往 →":
    - /url: /dashboard/stats
  - text: 📋
  - heading "考试管理" [level=3]
  - paragraph: 管理目标考试与倒计时
  - link "前往 →":
    - /url: /dashboard/exams
- alert
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-文章浏览与精读', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('http://localhost:3001', { waitUntil: 'domcontentloaded' });
  6  |   });
  7  | 
  8  |   test('正常浏览文章列表并进入精读页', async ({ page }) => {
  9  |     await expect(page.getByTestId('article-list')).toBeVisible({ timeout: 10000 });
  10 |     await page.getByTestId('article-item').first().click();
  11 |     await expect(page.getByTestId('original-article-tab')).toBeVisible();
  12 |     await page.getByTestId('deconstruction-tab').click();
  13 |     await expect(page.getByTestId('deconstruction-content')).toBeVisible();
  14 |   });
  15 | 
  16 |   test('文章列表为空时显示提示信息', async ({ page }) => {
> 17 |     await expect(page.getByText('暂无推送文章')).toBeVisible({ timeout: 5000 });
     |                                            ^ Error: expect(locator).toBeVisible() failed
  18 |   });
  19 | });
```