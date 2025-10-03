import { test, expect } from '@playwright/test'

test.describe('Desktop Navigation Test', () => {
  test('test desktop navigation links', async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1200, height: 800 })
    
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Wait for page to load
    await page.waitForTimeout(2000)
    
    // Test Features link (header navigation)
    const featuresLink = page.getByRole('navigation').getByRole('link', { name: 'Features' })
    await expect(featuresLink).toBeVisible()
    
    console.log('Clicking Features link...')
    await featuresLink.click()
    await page.waitForTimeout(2000)
    console.log(`URL after clicking Features: ${page.url()}`)
    
    if (page.url().includes('/features')) {
      console.log('✅ Desktop Features navigation works')
    } else {
      console.log('❌ Desktop Features navigation failed')
    }
    
    // Go back to homepage
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(1000)
    
    // Test Pricing link (header navigation)
    const pricingLink = page.getByRole('navigation').getByRole('link', { name: 'Pricing' })
    await expect(pricingLink).toBeVisible()
    
    console.log('Clicking Pricing link...')
    await pricingLink.click()
    await page.waitForTimeout(2000)
    console.log(`URL after clicking Pricing: ${page.url()}`)
    
    if (page.url().includes('/pricing')) {
      console.log('✅ Desktop Pricing navigation works')
    } else {
      console.log('❌ Desktop Pricing navigation failed')
    }
  })
})
