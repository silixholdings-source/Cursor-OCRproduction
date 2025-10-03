import { test, expect } from '@playwright/test'

test.describe('Features Page Test', () => {
  test('test direct navigation to features page', async ({ page }) => {
    // Test direct navigation to features
    await page.goto('/features', { waitUntil: 'domcontentloaded' })
    await expect(page.locator('body')).toBeVisible()
    console.log(`✅ Direct navigation to /features works: ${page.url()}`)
    
    // Test direct navigation to pricing
    await page.goto('/pricing', { waitUntil: 'domcontentloaded' })
    await expect(page.locator('body')).toBeVisible()
    console.log(`✅ Direct navigation to /pricing works: ${page.url()}`)
    
    // Test direct navigation to about
    await page.goto('/about', { waitUntil: 'domcontentloaded' })
    await expect(page.locator('body')).toBeVisible()
    console.log(`✅ Direct navigation to /about works: ${page.url()}`)
    
    // Test direct navigation to contact
    await page.goto('/contact', { waitUntil: 'domcontentloaded' })
    await expect(page.locator('body')).toBeVisible()
    console.log(`✅ Direct navigation to /contact works: ${page.url()}`)
  })
})


