# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 每日推送文章列表 >> TC-001: 文章列表正常加载并展示基本信息
- Location: testpilot-backend\generated\.runtime\a6bb9b81\test.spec.ts:12:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByTestId('article-list')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByTestId('article-list')

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
  - text: S
  - paragraph: Sally
  - button "退出"
- main:
  - heading "你好，Sally 👋" [level=1]
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
  3  | test.describe('每日推送文章列表', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('http://localhost:3001/dashboard', { waitUntil: 'domcontentloaded' });
  6  |   });
  7  | 
  8  |   test('环境验证: 页面加载成功', async ({ page }) => {
  9  |     await expect(page.getByTestId('page-container')).toBeVisible();
  10 |   });
  11 | 
  12 |   test('TC-001: 文章列表正常加载并展示基本信息', async ({ page }) => {
> 13 |     await expect(page.getByTestId('article-list')).toBeVisible();
     |                                                    ^ Error: expect(locator).toBeVisible() failed
  14 |     const cards = page.getByTestId('article-card');
  15 |     const count = await cards.count();
  16 |     expect(count).toBeGreaterThanOrEqual(10);
  17 |     const firstCard = cards.first();
  18 |     await expect(firstCard.getByTestId('article-title')).toBeVisible();
  19 |     await expect(firstCard.getByTestId('article-summary')).toBeVisible();
  20 |     await expect(firstCard.getByTestId('article-publish-time')).toBeVisible();
  21 |   });
  22 | });
```