test('placeholder', async ({page}) => {
  await page.goto('https://demo.playwright.dev/todomvc/');
  await page.waitForTimeout(1000);
});