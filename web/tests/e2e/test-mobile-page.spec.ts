import { test, expect } from '@playwright/test'

test.describe('Mobile Page Test', () => {
  test('test mobile page', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/mobile', { waitUntil: 'domcontentloaded' })
    
    console.log(`Mobile page: Status ${response?.status()}, URL: ${page.url()}`)

    expect(response?.ok()).toBeTruthy()
    expect(page.url()).toContain('/mobile')
    await expect(page.getByRole('heading', { name: 'Mobile Apps', level: 1 })).toBeVisible()
    console.log('✅ Mobile page is now working (Status: 200)')
    console.log(`   Page title: "${await page.title()}"`)
  })
})


