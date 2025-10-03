import { test, expect } from '@playwright/test'

test.describe('Footer Mobile Link Test', () => {
  test('test footer mobile apps link', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })

    console.log('Testing footer Mobile Apps link...')

    // Scroll to footer
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(1000)

    // Find and click the Mobile Apps link
    const mobileLink = page.getByRole('link', { name: 'Mobile Apps' }).first()
    await expect(mobileLink).toBeVisible()
    
    console.log('Clicking Mobile Apps link...')
    await mobileLink.click()
    await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
    
    const url = page.url()
    console.log(`URL after clicking Mobile Apps: ${url}`)
    
    expect(url).toContain('/mobile')
    console.log('✅ Footer Mobile Apps link works!')
  })
})


