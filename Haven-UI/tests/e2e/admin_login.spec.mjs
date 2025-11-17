import { test, expect } from '@playwright/test';

test('Admin unlock reveals RT-AI/Settings/Tests', async ({ page }) => {
  await page.goto('http://127.0.0.1:8005/haven-ui');
  // Should not show admin links by default
  await expect(page.locator('text=RT-AI')).toHaveCount(0);
  await expect(page.locator('text=Settings')).toHaveCount(0);
  await expect(page.locator('text=Test Manager')).toHaveCount(0);
  // Click unlock, fill password, and confirm links visible
  await page.click('button:has-text("Unlock")');
  await page.fill('#admin-password', process.env.HAVEN_ADMIN_PASSWORD || 'Haven');
  await page.click('#admin-login-submit');
  await expect(page.locator('text=RT-AI')).toHaveCount(1);
  await expect(page.locator('text=Settings')).toHaveCount(1);
  await expect(page.locator('text=Test Manager')).toHaveCount(1);
  // Logout and confirm hidden again
  await page.click('button:has-text("Logout")');
  await expect(page.locator('text=RT-AI')).toHaveCount(0);
});
