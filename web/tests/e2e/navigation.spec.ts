import { test, expect } from '@playwright/test'

test.describe('Navigation Links', () => {
  test('should navigate to all main pages without errors', async ({ page }) => {
    const pages = [
      { path: '/', name: 'Home' },
      { path: '/features', name: 'Features' },
      { path: '/pricing', name: 'Pricing' },
      { path: '/about', name: 'About' },
      { path: '/contact', name: 'Contact' },
      { path: '/auth/login', name: 'Login' },
      { path: '/auth/register', name: 'Register' },
      { path: '/dashboard', name: 'Dashboard' },
    ]

    for (const { path, name } of pages) {
      await test.step(`navigate to ${name} (${path})`, async () => {
        await page.goto(path, { waitUntil: 'domcontentloaded' })
        
        // Check that page loads without console errors
        const errors: string[] = []
        page.on('pageerror', e => errors.push(String(e)))
        page.on('console', msg => { 
          if (msg.type() === 'error') errors.push(msg.text()) 
        })
        
        // Wait for page to be ready
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
        
        // Check that body is visible (page loaded)
        await expect(page.locator('body')).toBeVisible()
        
        // Check for any console errors
        expect(errors.join('\n')).toBe('')
      })
    }
  })

  test('should have working header navigation links', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Test header navigation links
        const headerLinks = [
          { text: 'Features', href: '/features' },
          { text: 'Pricing', href: '/pricing' },
          { text: 'Integrations', href: '/integrations' },
          { text: 'Security', href: '/security' },
          { text: 'Support', href: '/support' },
        ]

    for (const { text, href } of headerLinks) {
      await test.step(`click header link: ${text}`, async () => {
        // Try to find the link in both desktop and mobile navigation
        let link = page.getByRole('link', { name: text }).first()
        
        // If not visible, try opening mobile menu
        if (!(await link.isVisible())) {
          const mobileMenuButton = page.getByRole('button', { name: /menu/i })
          if (await mobileMenuButton.isVisible()) {
            await mobileMenuButton.click()
            await page.waitForTimeout(500) // Wait for menu to open
          }
        }
        
        await expect(link).toBeVisible()
        
        // Click the link
        await link.click()
        
        // Wait for navigation with shorter timeout
        await page.waitForLoadState('domcontentloaded', { timeout: 3000 })
        
        // Check that we're on the expected page
        expect(page.url()).toContain(href)
      })
    }
  })

  test('should have working footer navigation links', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Scroll to footer
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    
    // Test footer links
    const footerLinks = [
      { text: 'Features', href: '/features' },
      { text: 'Pricing', href: '/pricing' },
      { text: 'About', href: '/about' },
      { text: 'Contact', href: '/contact' },
      { text: 'Privacy Policy', href: '/privacy' },
      { text: 'Terms of Service', href: '/terms' },
    ]

    for (const { text, href } of footerLinks) {
      await test.step(`click footer link: ${text}`, async () => {
        const link = page.getByRole('link', { name: text }).first()
        await expect(link).toBeVisible()
        
        // Click the link
        await link.click()
        
        // Wait for navigation with shorter timeout
        await page.waitForLoadState('domcontentloaded', { timeout: 3000 })
        
        // Check that we're on the expected page
        expect(page.url()).toContain(href)
        
        // Check that page loads without errors
        await expect(page.locator('body')).toBeVisible()
      })
    }
  })

  test('should have working CTA buttons', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Test "Start Free Trial" buttons
    const trialButtons = page.getByRole('button', { name: /Start Free Trial/i })
    const trialCount = await trialButtons.count()
    expect(trialCount).toBeGreaterThan(0)
    
    // Click first trial button
    await trialButtons.first().click()
    await page.waitForLoadState('domcontentloaded', { timeout: 3000 })
    
    // Should navigate to signup or trial page
    expect(page.url()).toMatch(/\/(signup|trial|auth\/register)/)
    
    // Go back to home
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Test "Watch Demo" buttons
    const demoButtons = page.getByRole('button', { name: /Watch Demo/i })
    const demoCount = await demoButtons.count()
    expect(demoCount).toBeGreaterThan(0)
    
    // Click first demo button
    await demoButtons.first().click()
    await page.waitForLoadState('domcontentloaded', { timeout: 3000 })
    
    // Should navigate to demo page or show modal
    await expect(page.locator('body')).toBeVisible()
  })

  test('should have working dashboard navigation', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Check that dashboard loads
    await expect(page.locator('body')).toBeVisible()
    
    // Test dashboard sidebar links
    const dashboardLinks = [
      'Dashboard',
      'Invoices', 
      'Approvals',
      'Vendors',
      'Users',
      'Analytics',
      'Settings'
    ]

    for (const linkText of dashboardLinks) {
      await test.step(`click dashboard link: ${linkText}`, async () => {
        const link = page.getByRole('link', { name: linkText }).first()
        if (await link.isVisible()) {
          await link.click()
          await page.waitForLoadState('networkidle', { timeout: 5000 })
          await expect(page.locator('body')).toBeVisible()
        }
      })
    }
  })
})
