import { test, expect } from '@playwright/test';

test('create new system with nested planet and moon', async ({ page }) => {
  await page.goto('/wizard');

  const randomName = 'E2E-SYS-' + Math.floor(Math.random() * 100000);
  await page.fill('input[placeholder="Name"], input[aria-label="Name"]', randomName);
  await page.fill('input[placeholder="X"]', '12');
  await page.fill('input[placeholder="Y"]', '-5');
  await page.fill('input[placeholder="Z"]', '3');
  await page.fill('input[placeholder="Region"], input[name="region"]', 'E2E-Region');
  await page.fill('textarea[aria-label="System description"]', 'E2E test system');

  // Add Planet
  await page.click('button:has-text("➕ Add Planet")');
  await page.fill('input[placeholder="Planet name"]', 'E2E-Planet-1');
  // select fauna and flora using selectOption
  await page.selectOption('select[aria-label="Planet Fauna"]', 'Abundant');
  await page.selectOption('select[aria-label="Planet Flora"]', 'Moderate');
  await page.fill('input[aria-label="Planet Materials"]', 'Ferrite,Gold');
  await page.fill('input[placeholder="Base location"]', 'Planetary Base');

  // Upload a photo for the planet
  const testFile = 'tests/e2e/test-photo.jpg';
  await page.setInputFiles('input[aria-label="Planet Photo"]', testFile);
  // Wait for the photo upload to complete and show the path in the UI
  await page.waitForResponse(response => response.url().includes('/api/photos') && response.status() === 200, { timeout: 5000 });

  // Add Moon inside Planet
  await page.click('button:has-text("➕ Add Moon")');
  await page.fill('input[placeholder="Moon name"]', 'E2E-Moon-1');
  await page.selectOption('select[aria-label="Moon Fauna"]', 'Low');
  await page.selectOption('select[aria-label="Moon Flora"]', 'Sparse');
  await page.fill('input[aria-label="Moon Materials"]', 'Emeril');
  await page.fill('input[aria-label="Moon Orbit Radius"]', '0.6');
  await page.fill('input[aria-label="Moon Orbit Speed"]', '0.03');

  // Save the moon modal first (important - modal Save commits moon to planet)
  await page.click('div:has-text("Add Moon") button:has-text("Save")');
  await page.waitForSelector('div:has-text("Add Moon")', { state: 'detached' });
  // Save the wizard (top-level Save button)
  await page.click('button.btn-primary');

  // Wait for navigation to systems list and confirm the system appears
  await page.waitForURL('**/systems');
  const exists = await page.isVisible(`text=${randomName}`);
  expect(exists).toBeTruthy();
});
