# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 生成登录会话快照
- Location: testpilot-backend\generated\.runtime\d7abf1b0\test.spec.ts:3:5

# Error details

```
TimeoutError: page.waitForURL: Timeout 15000ms exceeded.
=========================== logs ===========================
waiting for navigation to "http://localhost:3001/dashboard**" until "load"
  navigated to "http://localhost:3001/login"
============================================================
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e4]:
    - generic [ref=e5]:
      - heading "欢迎回来" [level=1] [ref=e6]
      - paragraph [ref=e7]: 登录考公大师，继续你的备考之旅
    - generic [ref=e8]:
      - generic [ref=e9]:
        - generic [ref=e10]: 邮箱
        - textbox "邮箱" [ref=e11]:
          - /placeholder: your@email.com
      - generic [ref=e12]:
        - generic [ref=e13]: 密码
        - textbox "密码" [ref=e14]:
          - /placeholder: ••••••••
      - button "登录" [ref=e15] [cursor=pointer]
    - paragraph [ref=e17]:
      - text: 还没有账号？
      - link "立即注册" [ref=e18] [cursor=pointer]:
        - /url: /register
  - alert [ref=e19]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('生成登录会话快照', async ({ page }) => {
  4  |   // 1. 访问登录页
  5  |   await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });
  6  | 
  7  |   // 2. 填入凭证
  8  |   await (page.getByRole('textbox', { name: '邮箱' })).fill('tester@kaogong.com');
  9  |   await (page.getByRole('textbox', { name: '密码' })).fill('Test1234!');
  10 | 
  11 |   // 3. 点击提交
  12 |   await (page.getByRole('button', { name: '登录' })).click();
  13 | 
  14 |   // 4. 等待登录成功
> 15 |   await page.waitForURL('http://localhost:3001/dashboard**', { timeout: 15000 });
     |              ^ TimeoutError: page.waitForURL: Timeout 15000ms exceeded.
  16 | 
  17 |   // 5. 保存会话快照
  18 |   await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/2/profile-8.json' });
  19 | });
  20 | 
```