import { test, expect } from '@playwright/test'

const baseUrl = 'http://localhost:3000'

test.describe('Comprehensive Navigation Test', () => {
  test('test all navigation elements on homepage', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })

    // Test hero section CTA buttons
    await test.step('Test hero CTA buttons', async () => {
      // Target LinkButton components specifically (they render as links)
      const startTrialLinks = page.getByRole('link', { name: /Start Free Trial/i })
      const trialCount = await startTrialLinks.count()
      expect(trialCount).toBeGreaterThan(0)

      // Click first Start Free Trial link (LinkButton component)
      await startTrialLinks.first().click()
      await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
      expect(page.url()).toContain('/auth/register')

      // Go back to home
      await page.goto('/', { waitUntil: 'domcontentloaded' })

      // Test Watch Demo button
      const demoLinks = page.getByRole('link', { name: /Watch Demo/i })
      const demoCount = await demoLinks.count()
      expect(demoCount).toBeGreaterThan(0)

      await demoLinks.first().click()
      await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
      expect(page.url()).toContain('/demo')

      // Go back to home
      await page.goto('/', { waitUntil: 'domcontentloaded' })
    })

    // Test header navigation links
    await test.step('Test header navigation links', async () => {
      const headerLinks = [
        { text: 'Features', href: '/features' },
        { text: 'How It Works', href: '/features' },
        { text: 'Pricing', href: '/pricing' },
        { text: 'About', href: '/about' },
        { text: 'Contact', href: '/contact' },
      ]

      for (const { text, href } of headerLinks) {
        console.log(`Testing header link: ${text}`)
        
        // Try to find the link in desktop navigation first
        let link = page.getByRole('link', { name: text }).first()

        // If not visible, try opening mobile menu
        if (!(await link.isVisible())) {
          console.log(`${text} not visible, trying mobile menu...`)
          const mobileMenuButton = page.getByRole('button', { name: /menu/i })
          if (await mobileMenuButton.isVisible()) {
            console.log('Opening mobile menu...')
            await mobileMenuButton.click()
            await page.waitForTimeout(1000)
            // Try to find the link again after opening mobile menu
            link = page.getByRole('link', { name: text }).first()
          }
        }

        // If still not visible, skip this link
        if (!(await link.isVisible())) {
          console.log(`${text} still not visible, skipping...`)
          continue
        }

        await link.click()
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
        
        console.log(`URL after clicking ${text}: ${page.url()}`)
        expect(page.url()).toContain(href)

        // Go back to home
        await page.goto('/', { waitUntil: 'domcontentloaded' })
      }
    })

    // Test header auth buttons
    await test.step('Test header auth buttons', async () => {
      // Test Sign In button
      const signInButton = page.getByRole('button', { name: /Sign In/i })
      if (await signInButton.isVisible()) {
        await signInButton.click()
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
        expect(page.url()).toContain('/auth/login')
        await page.goto('/', { waitUntil: 'domcontentloaded' })
      }

      // Test Get Started button
      const getStartedButton = page.getByRole('button', { name: /Get Started/i })
      if (await getStartedButton.isVisible()) {
        await getStartedButton.click()
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
        expect(page.url()).toContain('/auth/register')
        await page.goto('/', { waitUntil: 'domcontentloaded' })
      }
    })

    // Test footer navigation links
    await test.step('Test footer navigation links', async () => {
      // Scroll to footer
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
      await page.waitForTimeout(1000)

      const footerLinks = [
        { text: 'Features', href: '/features' },
        { text: 'Pricing', href: '/pricing' },
        { text: 'About Us', href: '/about' },
        { text: 'Contact Us', href: '/contact' },
        { text: 'Privacy Policy', href: '/privacy' },
        { text: 'Terms of Service', href: '/terms' },
        { text: 'Partners', href: '/partners' },
      ]

      for (const { text, href } of footerLinks) {
        console.log(`Testing footer link: ${text}`)
        
        const link = page.getByRole('link', { name: text }).first()
        await expect(link).toBeVisible()
        await link.click()
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
        
        console.log(`URL after clicking ${text}: ${page.url()}`)
        expect(page.url()).toContain(href)

        // Go back to home
        await page.goto('/', { waitUntil: 'domcontentloaded' })
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
        await page.waitForTimeout(500)
      }
    })

    // Test CTA section buttons
    await test.step('Test CTA section buttons', async () => {
      // Scroll to CTA section
      await page.evaluate(() => {
        const ctaSection = document.querySelector('section:last-of-type')
        if (ctaSection) {
          ctaSection.scrollIntoView({ behavior: 'smooth' })
        }
      })
      await page.waitForTimeout(1000)

      // Test Schedule Demo button
      const scheduleDemoButton = page.getByRole('button', { name: /Schedule Demo/i })
      if (await scheduleDemoButton.isVisible()) {
        await scheduleDemoButton.click()
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
        expect(page.url()).toContain('/contact')
        await page.goto('/', { waitUntil: 'domcontentloaded' })
      }
    })
  })
})
