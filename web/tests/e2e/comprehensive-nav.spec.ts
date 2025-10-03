import { test, expect } from '@playwright/test'

test.describe('Comprehensive Navigation Test', () => {
  test('verify all main navigation works', async ({ page }) => {
    // Test homepage CTA buttons
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(2000)
    
    // Test Start Free Trial button
    const trialButton = page.getByRole('button', { name: /Start Free Trial/i }).first()
    await trialButton.click()
    await page.waitForTimeout(2000)
    expect(page.url()).toContain('/auth/register')
    console.log('✅ Homepage Start Free Trial button works')
    
    // Go back to homepage
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(1000)
    
    // Test Watch Demo button
    const demoButton = page.getByRole('button', { name: /Watch Demo/i }).first()
    await demoButton.click()
    await page.waitForTimeout(2000)
    expect(page.url()).toContain('/demo')
    console.log('✅ Homepage Watch Demo button works')
    
    // Go back to homepage
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(1000)
    
    // Test header navigation (desktop viewport)
    await page.setViewportSize({ width: 1200, height: 800 })
    
    // Test Features link
    const featuresLink = page.getByRole('navigation').getByRole('link', { name: 'Features' })
    await featuresLink.click()
    await page.waitForTimeout(2000)
    expect(page.url()).toContain('/features')
    console.log('✅ Header Features link works')
    
    // Go back to homepage
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(1000)
    
    // Test Pricing link
    const pricingLink = page.getByRole('navigation').getByRole('link', { name: 'Pricing' })
    await pricingLink.click()
    await page.waitForTimeout(2000)
    expect(page.url()).toContain('/pricing')
    console.log('✅ Header Pricing link works')
    
    // Go back to homepage
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(1000)
    
    // Test About link
    const aboutLink = page.getByRole('navigation').getByRole('link', { name: 'About' })
    await aboutLink.click()
    await page.waitForTimeout(2000)
    expect(page.url()).toContain('/about')
    console.log('✅ Header About link works')
    
    // Go back to homepage
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(1000)
    
    // Test Contact link
    const contactLink = page.getByRole('navigation').getByRole('link', { name: 'Contact' })
    await contactLink.click()
    await page.waitForTimeout(2000)
    expect(page.url()).toContain('/contact')
    console.log('✅ Header Contact link works')
    
    // Test mobile navigation
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(1000)
    
    // Open mobile menu
    const mobileMenuButton = page.getByRole('button', { name: /menu/i })
    await mobileMenuButton.click()
    await page.waitForTimeout(500)
    
    // Test mobile Features link
    const mobileFeaturesLink = page.getByRole('link', { name: 'Features' }).last()
    await mobileFeaturesLink.click()
    await page.waitForTimeout(2000)
    expect(page.url()).toContain('/features')
    console.log('✅ Mobile Features link works')
    
    console.log('🎉 All navigation tests passed!')
  })
})


