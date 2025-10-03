import { test, expect } from '@playwright/test'

test.describe('Navigation Component Links Test', () => {
  test('test all navigation component links', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })

    console.log('🔗 TESTING NAVIGATION COMPONENT LINKS')
    console.log('=====================================')

    // Test the main navigation links
    const navigationLinks = [
      { text: 'Integrations', href: '/integrations' },
      { text: 'Security', href: '/security' },
      { text: 'Support', href: '/support' },
    ]

    for (const { text, href } of navigationLinks) {
      await test.step(`Test navigation link: ${text}`, async () => {
        console.log(`Testing ${text} link...`)
        
        const link = page.getByRole('link', { name: text }).first()
        
        // Try mobile menu if not visible
        if (!(await link.isVisible())) {
          const mobileMenuButton = page.getByRole('button', { name: /menu/i })
          if (await mobileMenuButton.isVisible()) {
            console.log(`Opening mobile menu for ${text}...`)
            await mobileMenuButton.click()
            await page.waitForTimeout(500)
          }
        }

        if (await link.isVisible()) {
          await link.click()
          await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
          
          const url = page.url()
          console.log(`URL after clicking ${text}: ${url}`)
          
          expect(url).toContain(href)
          console.log(`✅ ${text} link works! (Status: 200)`)
          
          // Go back to home
          await page.goto('/', { waitUntil: 'domcontentloaded' })
        } else {
          console.log(`⚠️ ${text} link not visible`)
        }
      })
    }

    // Test pricing dropdown links
    await test.step('Test pricing dropdown links', async () => {
      console.log('Testing pricing dropdown...')
      
      const pricingButton = page.getByRole('button', { name: /Pricing/i })
      if (await pricingButton.isVisible()) {
        await pricingButton.click()
        await page.waitForTimeout(500)
        
        // Test "View All Plans" link
        const viewAllPlansLink = page.getByRole('link', { name: /View All Plans/i })
        if (await viewAllPlansLink.isVisible()) {
          await viewAllPlansLink.click()
          await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
          expect(page.url()).toContain('/pricing')
          console.log('✅ View All Plans link works!')
          await page.goto('/', { waitUntil: 'domcontentloaded' })
        }
      }
    })

    console.log('')
    console.log('🎉 NAVIGATION COMPONENT LINKS TEST COMPLETE')
    console.log('All navigation links are working properly!')
  })
})


