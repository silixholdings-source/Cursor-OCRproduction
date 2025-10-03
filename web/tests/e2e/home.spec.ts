import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test('should display the main heading', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Automate Invoice Processing with')
    await expect(page.getByRole('heading', { level: 1 })).toContainText('AI Power')
  })

  test('should display the hero section with CTAs', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    await expect(page.getByRole('button', { name: /Start Free Trial/i }).first()).toBeVisible()
    await expect(page.getByRole('button', { name: /Watch Demo/i })).toBeVisible()
  })

  test('should display the features section', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    const sectionCount = await page.locator('section').count()
    expect(sectionCount).toBeGreaterThan(0)
    await expect(page.getByText('Why Choose AI ERP SaaS?')).toBeVisible()
  })

  test('should display the stats section', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await expect(page.getByText('10,000+')).toBeVisible()
    await expect(page.getByText('Active Users')).toBeVisible()
    await expect(page.getByText('95%', { exact: true }).first()).toBeVisible()
    await expect(page.getByText('Accuracy Rate', { exact: true }).first()).toBeVisible()
  })

  test('should display the CTA section', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await expect(page.getByText('Ready to Transform Your Invoice Processing?')).toBeVisible()
    await expect(page.getByRole('button', { name: /Start Free Trial/i }).first()).toBeVisible()
    await expect(page.getByRole('button', { name: /Schedule Demo/i })).toBeVisible()
  })

  test('should be responsive', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.locator('body')).toBeVisible()
    await page.setViewportSize({ width: 1440, height: 900 })
    await expect(page.locator('body')).toBeVisible()
  })
})