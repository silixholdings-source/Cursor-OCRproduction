import { test, expect } from '@playwright/test'

test.describe('Simple Navigation Test', () => {
  test('test direct link navigation', async ({ page }) => {
    // Test direct navigation to auth/register
    await page.goto('/auth/register', { waitUntil: 'domcontentloaded' })
    await expect(page.locator('body')).toBeVisible()
    console.log(`✅ Direct navigation to /auth/register works: ${page.url()}`)
    
    // Test direct navigation to demo
    await page.goto('/demo', { waitUntil: 'domcontentloaded' })
    await expect(page.locator('body')).toBeVisible()
    console.log(`✅ Direct navigation to /demo works: ${page.url()}`)
  })

  test('test homepage button click with manual navigation', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Wait for page to fully load
    await page.waitForTimeout(3000)
    
    // Find the Start Free Trial button
    const trialButton = page.getByRole('button', { name: /Start Free Trial/i }).first()
    await expect(trialButton).toBeVisible()
    
    // Check if it's inside a link
    const buttonParent = trialButton.locator('..')
    const isInsideLink = await buttonParent.evaluate(el => el.tagName === 'A')
    console.log(`Button is inside link: ${isInsideLink}`)
    
    if (isInsideLink) {
      const href = await buttonParent.getAttribute('href')
      console.log(`Parent link href: ${href}`)
      
      // Try clicking the parent link instead of the button
      await buttonParent.click()
      await page.waitForTimeout(2000)
      console.log(`URL after clicking parent link: ${page.url()}`)
      
      if (page.url().includes('/auth/register')) {
        console.log('✅ Navigation successful via parent link click')
      } else {
        console.log('❌ Navigation failed via parent link click')
      }
    }
  })
})


