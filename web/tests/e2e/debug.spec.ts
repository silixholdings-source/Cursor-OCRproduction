import { test, expect } from '@playwright/test'

test.describe('Debug Navigation', () => {
  test('debug CTA buttons', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Wait for page to fully load
    await page.waitForTimeout(2000)
    
    // Check if buttons exist
    const allButtons = await page.locator('button').count()
    console.log(`Total buttons found: ${allButtons}`)
    
    // Check for Start Free Trial buttons specifically
    const trialButtons = page.getByRole('button', { name: /Start Free Trial/i })
    const trialCount = await trialButtons.count()
    console.log(`Start Free Trial buttons found: ${trialCount}`)
    
    // Check for any buttons with "Start" text
    const startButtons = page.getByText(/Start/i)
    const startCount = await startButtons.count()
    console.log(`Buttons with "Start" text: ${startCount}`)
    
    // Check for links
    const allLinks = await page.locator('a').count()
    console.log(`Total links found: ${allLinks}`)
    
    // Check for auth/register links
    const authLinks = page.getByRole('link', { href: /auth\/register/ })
    const authCount = await authLinks.count()
    console.log(`Auth/register links found: ${authCount}`)
    
    // Take a screenshot
    await page.screenshot({ path: 'debug-homepage.png' })
    
    // Try to find any button and click it
    if (trialCount > 0) {
      console.log('Clicking first Start Free Trial button...')
      await trialButtons.first().click()
      await page.waitForTimeout(1000)
      console.log(`URL after click: ${page.url()}`)
    } else {
      console.log('No Start Free Trial buttons found')
    }
  })
})



