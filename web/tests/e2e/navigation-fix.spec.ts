import { test, expect } from '@playwright/test'

test.describe('Navigation Fix Verification', () => {
  test('CTA buttons should navigate correctly', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Test Start Free Trial button
    const trialButton = page.getByRole('button', { name: /Start Free Trial/i }).first()
    await expect(trialButton).toBeVisible()
    
    // Click and wait for navigation
    await Promise.all([
      page.waitForURL('**/auth/register**', { timeout: 10000 }),
      trialButton.click()
    ])
    
    console.log(`✅ Start Free Trial button navigated to: ${page.url()}`)
    expect(page.url()).toContain('/auth/register')
    
    // Go back to homepage
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Test Watch Demo button
    const demoButton = page.getByRole('button', { name: /Watch Demo/i }).first()
    await expect(demoButton).toBeVisible()
    
    // Click and wait for navigation
    await Promise.all([
      page.waitForURL('**/demo**', { timeout: 10000 }),
      demoButton.click()
    ])
    
    console.log(`✅ Watch Demo button navigated to: ${page.url()}`)
    expect(page.url()).toContain('/demo')
  })

  test('CTA section buttons should navigate correctly', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Scroll to bottom CTA section
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(1000)
    
    // Test bottom Start Free Trial button
    const bottomTrialButtons = page.getByRole('button', { name: /Start Free Trial/i })
    const trialCount = await bottomTrialButtons.count()
    expect(trialCount).toBeGreaterThan(1) // Should have at least 2 (top and bottom)
    
    // Click the second one (bottom) and wait for navigation
    await Promise.all([
      page.waitForURL('**/auth/register**', { timeout: 10000 }),
      bottomTrialButtons.nth(1).click()
    ])
    
    console.log(`✅ Bottom Start Free Trial button navigated to: ${page.url()}`)
    expect(page.url()).toContain('/auth/register')
  })
})
