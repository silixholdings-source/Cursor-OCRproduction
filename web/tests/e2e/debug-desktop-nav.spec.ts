import { test, expect } from '@playwright/test'

test.describe('Debug Desktop Navigation', () => {
  test('debug CTA button navigation on desktop browsers', async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1200, height: 800 })
    
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Wait for page to fully load
    await page.waitForTimeout(3000)
    
    // Check for JavaScript errors
    const errors: string[] = []
    page.on('pageerror', e => errors.push(String(e)))
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    
    // Debug button structure
    const allButtons = page.locator('button')
    const buttonCount = await allButtons.count()
    console.log(`Total buttons found: ${buttonCount}`)
    
    const trialButtons = page.getByRole('button', { name: /Start Free Trial/i })
    const trialCount = await trialButtons.count()
    console.log(`Start Free Trial buttons found: ${trialCount}`)
    
    if (trialCount > 0) {
      const firstButton = trialButtons.first()
      await expect(firstButton).toBeVisible()
      
      // Check if button is inside a link
      const buttonParent = firstButton.locator('..')
      const isInsideLink = await buttonParent.evaluate(el => el.tagName === 'A')
      console.log(`Button is inside link: ${isInsideLink}`)
      
      if (isInsideLink) {
        const href = await buttonParent.getAttribute('href')
        console.log(`Parent link href: ${href}`)
        
        // Try clicking the parent link instead
        console.log('Attempting to click parent link...')
        await buttonParent.click()
        await page.waitForTimeout(3000)
        console.log(`URL after clicking parent link: ${page.url()}`)
      } else {
        console.log('Button is not inside a link - this is the problem!')
      }
      
      // Try clicking the button directly
      console.log('Attempting to click button directly...')
      await page.goto('/', { waitUntil: 'domcontentloaded' })
      await page.waitForTimeout(2000)
      await firstButton.click()
      await page.waitForTimeout(3000)
      console.log(`URL after clicking button: ${page.url()}`)
    }
    
    // Check for JavaScript errors
    console.log('=== JavaScript Errors ===')
    errors.forEach(error => console.log(`ERROR: ${error}`))
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'debug-desktop-nav.png' })
  })
})


