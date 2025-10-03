import { test, expect } from '@playwright/test'

test.describe('Debug Rendering', () => {
  test('debug button rendering on mobile', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Wait for page to fully render
    await page.waitForTimeout(3000)
    
    // Take screenshot
    await page.screenshot({ path: 'debug-mobile-rendering.png' })
    
    // Check all buttons
    const allButtons = page.locator('button')
    const buttonCount = await allButtons.count()
    console.log(`Total buttons found: ${buttonCount}`)
    
    // Check all links
    const allLinks = page.locator('a')
    const linkCount = await allLinks.count()
    console.log(`Total links found: ${linkCount}`)
    
    // Check for Start Free Trial text in any element
    const startFreeTrialElements = page.getByText('Start Free Trial')
    const startFreeTrialCount = await startFreeTrialElements.count()
    console.log(`Start Free Trial text elements found: ${startFreeTrialCount}`)
    
    // Check for auth/register links
    const authRegisterLinks = page.locator('a[href="/auth/register"]')
    const authRegisterCount = await authRegisterLinks.count()
    console.log(`Auth/register links found: ${authRegisterCount}`)
    
    // Check page HTML structure
    const bodyHTML = await page.locator('body').innerHTML()
    console.log('Body HTML length:', bodyHTML.length)
    
    // Look for specific button classes
    const buttonWithClasses = page.locator('button.inline-flex')
    const buttonWithClassesCount = await buttonWithClasses.count()
    console.log(`Buttons with inline-flex class: ${buttonWithClassesCount}`)
    
    // Check if there are any hidden elements
    const hiddenElements = page.locator('[style*="display: none"], [style*="visibility: hidden"]')
    const hiddenCount = await hiddenElements.count()
    console.log(`Hidden elements found: ${hiddenCount}`)
  })
})



