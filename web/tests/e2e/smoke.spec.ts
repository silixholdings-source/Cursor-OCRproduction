import { test, expect } from '@playwright/test';

const baseUrl = process.env.BASE_URL ?? 'http://localhost:3000';

// Public pages that should load without auth
const pages = ['/', '/features', '/pricing', '/about', '/contact'];

test.describe('Smoke navigation', () => {
  for (const path of pages) {
    test(`navigates ${path} without console errors`, async ({ page }) => {
      const errors: string[] = [];
      page.on('pageerror', (e) => errors.push(String(e)));
      page.on('console', (msg) => { if (msg.type() === 'error') errors.push(msg.text()); });

      const response = await page.goto(`${baseUrl}${path}`, { waitUntil: 'networkidle' });

      expect(response?.ok(), `HTTP not ok for ${path}: ${response?.status()}`).toBeTruthy();
      await expect(page.locator('body')).toBeVisible();

      const clickable = page.locator('a, button').first();
      if (await clickable.isVisible()) {
        await clickable.hover();
      }

      expect(errors.join('\n')).toBe('');
    });
  }
});

