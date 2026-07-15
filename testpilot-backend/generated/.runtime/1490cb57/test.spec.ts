import { test, expect } from "@playwright/test";

test("goto test", async ({ page }) => {
  await page.goto("http://localhost:3001/login", { waitUntil: "domcontentloaded" });
  await expect(page.locator("body")).toBeVisible();
});
