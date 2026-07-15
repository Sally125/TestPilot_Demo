# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 生成登录会话快照（自定义脚本）
- Location: testpilot-backend\generated\.runtime\12641fe7\test.spec.ts:3:5

# Error details

```
Test timeout of 60000ms exceeded.
```

```
Error: locator.fill: Test timeout of 60000ms exceeded.
Call log:
  - waiting for getByPlaceholder('邮箱')

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
  3  | test('生成登录会话快照（自定义脚本）', async ({ page }) => {
  4  |   // ===== 用户自定义登录代码 开始 =====
  5  |   // 登录脚本模板 - 请根据实际页面修改
  6  | await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });
  7  | 
  8  | // 填写凭证（请修改为实际的账号密码和选择器）
> 9  | await page.getByPlaceholder('邮箱').fill('huangkx1225@163.com');
     |                                   ^ Error: locator.fill: Test timeout of 60000ms exceeded.
  10 | await page.getByPlaceholder('密码').fill('123456');
  11 | 
  12 | // 点击登录按钮
  13 | await page.getByRole('button', { name: '登录' }).click();
  14 | 
  15 | // 等待登录成功（URL跳转或元素出现）
  16 | await page.waitForURL('**/dashboard**', { timeout: 10000 });
  17 |   // ===== 用户自定义登录代码 结束 =====
  18 | 
  19 |   // 自动追加：保存会话快照
  20 |   await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/2/profile-8.json' });
  21 | });
  22 | 
```