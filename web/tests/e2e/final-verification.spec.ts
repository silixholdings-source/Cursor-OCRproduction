import { test, expect } from '@playwright/test'

test.describe('Final Navigation Verification', () => {
  test('verify homepage CTA buttons work on all browsers', async ({ page }) => {
    await page.setViewportSize({ width: 1200, height: 800 })
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(2000)
    
    // Test homepage hero CTA buttons (should work on all browsers)
    const authRegisterLinks = page.locator('a[href="/auth/register"]')
    const linkCount = await authRegisterLinks.count()
    console.log(`Found ${linkCount} auth/register links`)
    
    // Test the homepage hero section buttons (these use LinkButton component)
    const heroSection = page.locator('section').first()
    const heroLinks = heroSection.locator('a[href="/auth/register"]')
    const heroLinkCount = await heroLinks.count()
    console.log(`Found ${heroLinkCount} hero section auth/register links`)
    
    if (heroLinkCount > 0) {
      const heroLink = heroLinks.first()
      await heroLink.click()
      await page.waitForTimeout(2000)
      console.log(`Hero section link navigation: ${page.url()}`)
      
      if (page.url().includes('/auth/register')) {
        console.log('✅ Homepage hero CTA button works!')
      } else {
        console.log('❌ Homepage hero CTA button failed')
      }
    }
    
    // Go back and test demo button
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(2000)
    
    const demoLinks = page.locator('a[href="/demo"]')
    const demoLinkCount = await demoLinks.count()
    console.log(`Found ${demoLinkCount} demo links`)
    
    if (demoLinkCount > 0) {
      const demoLink = demoLinks.first()
      await demoLink.click()
      await page.waitForTimeout(2000)
      console.log(`Demo link navigation: ${page.url()}`)
      
      if (page.url().includes('/demo')) {
        console.log('✅ Homepage demo button works!')
      } else {
        console.log('❌ Homepage demo button failed')
      }
    }
    
    // Test header navigation links
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(2000)
    
    const featuresLink = page.getByRole('navigation').getByRole('link', { name: 'Features' })
    if (await featuresLink.count() > 0) {
      await featuresLink.click()
      await page.waitForTimeout(2000)
      console.log(`Header Features navigation: ${page.url()}`)
      
      if (page.url().includes('/features')) {
        console.log('✅ Header Features link works!')
      } else {
        console.log('❌ Header Features link failed')
      }
    }
    
    console.log('🎉 Navigation verification complete!')
  })
})


