import { test, expect } from '@playwright/test'

test.describe('Link Navigation Test', () => {
  test('test direct link clicking', async ({ page }) => {
    await page.setViewportSize({ width: 1200, height: 800 })
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(3000)
    
    // Test the first auth/register link directly
    const authRegisterLinks = page.locator('a[href="/auth/register"]')
    const linkCount = await authRegisterLinks.count()
    console.log(`Found ${linkCount} auth/register links`)
    
    if (linkCount > 0) {
      const firstLink = authRegisterLinks.first()
      const linkText = await firstLink.textContent()
      console.log(`Clicking link with text: "${linkText}"`)
      
      await firstLink.click()
      await page.waitForTimeout(3000)
      console.log(`URL after clicking link: ${page.url()}`)
      
      if (page.url().includes('/auth/register')) {
        console.log('✅ Direct link navigation works!')
      } else {
        console.log('❌ Direct link navigation failed')
      }
    }
    
    // Go back and test the second link
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(2000)
    
    if (linkCount > 1) {
      const secondLink = authRegisterLinks.nth(1)
      const linkText = await secondLink.textContent()
      console.log(`Clicking second link with text: "${linkText}"`)
      
      await secondLink.click()
      await page.waitForTimeout(3000)
      console.log(`URL after clicking second link: ${page.url()}`)
      
      if (page.url().includes('/auth/register')) {
        console.log('✅ Second link navigation works!')
      } else {
        console.log('❌ Second link navigation failed')
      }
    }
  })
})


