import { test, expect } from '@playwright/test'

test.describe('JavaScript Error Check', () => {
  test('check for JavaScript errors on homepage', async ({ page }) => {
    const errors: string[] = []
    const warnings: string[] = []
    
    page.on('pageerror', e => errors.push(String(e)))
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text())
      if (msg.type() === 'warning') warnings.push(msg.text())
    })
    
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Wait a bit for any async errors
    await page.waitForTimeout(2000)
    
    console.log('=== JavaScript Errors ===')
    errors.forEach(error => console.log(`ERROR: ${error}`))
    
    console.log('=== JavaScript Warnings ===')
    warnings.forEach(warning => console.log(`WARNING: ${warning}`))
    
    // Check if buttons are actually clickable
    const trialButton = page.getByRole('button', { name: /Start Free Trial/i }).first()
    await expect(trialButton).toBeVisible()
    
    // Check if the button is inside a link
    const buttonParent = trialButton.locator('..')
    const isInsideLink = await buttonParent.evaluate(el => el.tagName === 'A')
    console.log(`Button is inside link: ${isInsideLink}`)
    
    // Check the href of the parent link
    if (isInsideLink) {
      const href = await buttonParent.getAttribute('href')
      console.log(`Parent link href: ${href}`)
    }
    
    // Try clicking and see what happens
    console.log('Attempting to click button...')
    await trialButton.click()
    await page.waitForTimeout(2000)
    console.log(`URL after click: ${page.url()}`)
    
    // Should not have JavaScript errors
    expect(errors).toEqual([])
  })
})



