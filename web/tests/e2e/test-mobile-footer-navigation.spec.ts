import { test, expect } from '@playwright/test'

test.describe('Mobile Footer Navigation Test', () => {
  test('test mobile footer link navigation', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })

    console.log('Testing Mobile Apps footer link navigation...')

    // Scroll to footer
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(1000)

    // Find and click the Mobile Apps link
    const mobileLink = page.getByRole('link', { name: 'Mobile Apps' }).first()
    await expect(mobileLink).toBeVisible()
    
    const href = await mobileLink.getAttribute('href')
    console.log(`Mobile Apps link href: ${href}`)
    
    await mobileLink.click()
    await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
    
    const url = page.url()
    console.log(`Final URL: ${url}`)
    
    // Verify we're on the mobile page
    expect(url).toContain('/mobile')
    await expect(page.getByRole('heading', { name: 'Mobile Apps', level: 1 })).toBeVisible()
    
    console.log('✅ Mobile Apps footer link navigation works!')
  })
})


