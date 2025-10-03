import { test, expect } from '@playwright/test'

test.describe('Pricing Page Test', () => {
  test('test pricing page loads correctly', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/pricing', { waitUntil: 'domcontentloaded' })
    
    console.log(`Pricing page: Status ${response?.status()}, URL: ${page.url()}`)

    expect(response?.ok()).toBeTruthy()
    expect(page.url()).toContain('/pricing')
    
    // Check if pricing page has content
    const body = page.locator('body')
    await expect(body).toBeVisible()
    
    console.log('✅ Pricing page loads correctly (Status: 200)')
    console.log(`   Page title: "${await page.title()}"`)
  })
})


