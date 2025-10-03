import { test, expect } from '@playwright/test'

test.describe('3-Day Trial Functionality Test', () => {
  test('should display 3-day trial period across all pages', async ({ page }) => {
    const pagesToCheck = [
      { url: 'http://localhost:3000', name: 'Homepage' },
      { url: 'http://localhost:3000/pricing', name: 'Pricing' },
      { url: 'http://localhost:3000/roi-calculator', name: 'ROI Calculator' },
      { url: 'http://localhost:3000/trial-info', name: 'Trial Info' }
    ]
    
    for (const pageInfo of pagesToCheck) {
      await page.goto(pageInfo.url, { waitUntil: 'domcontentloaded' })
      
      // Check for 3-day trial mentions
      await expect(page.getByText('3-day free trial')).toBeVisible()
      
      // Should not find any 30-day or 14-day trial mentions
      await expect(page.getByText('30-day free trial')).not.toBeVisible()
      await expect(page.getByText('14-day free trial')).not.toBeVisible()
      
      console.log(`✅ ${pageInfo.name} shows 3-day trial period`)
    }
  })
  
  test('should show trial countdown in dashboard when authenticated', async ({ page }) => {
    // Login with demo credentials
    await page.goto('http://localhost:3000/auth/login', { waitUntil: 'domcontentloaded' })
    await page.fill('input[type="email"]', 'demo@example.com')
    await page.fill('input[type="password"]', 'password')
    await page.click('button[type="submit"]')
    
    // Wait for dashboard to load
    await page.waitForURL('**/dashboard', { timeout: 10000 })
    
    // Check that trial banner is visible
    await expect(page.getByText(/day.*left in trial|Trial expires/i)).toBeVisible()
    
    // Check for upgrade button
    await expect(page.getByRole('button', { name: /View Plans|Upgrade/i })).toBeVisible()
    
    console.log('✅ Trial countdown banner is displayed in dashboard')
  })
  
  test('should show correct trial status for new registration', async ({ page }) => {
    await page.goto('http://localhost:3000/auth/register?trial=true', { waitUntil: 'domcontentloaded' })
    
    // Check registration page shows 3-day trial
    await expect(page.getByText('Start Your Free 3-Day Trial')).toBeVisible()
    await expect(page.getByText('You\'re starting a 3-day free trial')).toBeVisible()
    
    console.log('✅ Registration page shows correct 3-day trial messaging')
  })
  
  test('should display pricing plans with 3-day trial buttons', async ({ page }) => {
    await page.goto('http://localhost:3000/pricing', { waitUntil: 'domcontentloaded' })
    
    // Check that pricing plan buttons show 3-day trial
    const trialButtons = page.getByText(/Start 3-day free trial/i)
    const buttonCount = await trialButtons.count()
    
    // Should have multiple pricing plan buttons
    expect(buttonCount).toBeGreaterThan(0)
    
    console.log(`✅ Found ${buttonCount} pricing plan buttons with 3-day trial`)
  })
  
  test('should handle trial expiration logic correctly', async ({ page }) => {
    // Mock expired trial by setting localStorage with past date
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    const pastDate = new Date()
    pastDate.setDate(pastDate.getDate() - 1) // Yesterday
    
    await page.evaluate((expiredDate) => {
      localStorage.setItem('auth_user', JSON.stringify({
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'admin'
      }))
      localStorage.setItem('auth_company', JSON.stringify({
        id: '1',
        name: 'Test Company',
        max_users: 10,
        max_storage_gb: 100,
        plan: 'trial',
        is_trial: true,
        trial_ends_at: expiredDate
      }))
    }, pastDate.toISOString())
    
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Should show trial expired banner
    await expect(page.getByText('Trial Expired')).toBeVisible()
    await expect(page.getByText('Upgrade Now')).toBeVisible()
    
    console.log('✅ Trial expiration logic works correctly')
  })
  
  test('should show trial warning for last day', async ({ page }) => {
    // Mock trial expiring today
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    const today = new Date()
    today.setHours(23, 59, 59, 999) // End of today
    
    await page.evaluate((expiryDate) => {
      localStorage.setItem('auth_user', JSON.stringify({
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'admin'
      }))
      localStorage.setItem('auth_company', JSON.stringify({
        id: '1',
        name: 'Test Company',
        max_users: 10,
        max_storage_gb: 100,
        plan: 'trial',
        is_trial: true,
        trial_ends_at: expiryDate
      }))
    }, today.toISOString())
    
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Should show urgent trial warning
    await expect(page.getByText(/Trial expires today|0 day.*left/i)).toBeVisible()
    
    console.log('✅ Last day trial warning works correctly')
  })
  
  test('should have working upgrade buttons from trial banner', async ({ page }) => {
    // Login and go to dashboard
    await page.goto('http://localhost:3000/auth/login', { waitUntil: 'domcontentloaded' })
    await page.fill('input[type="email"]', 'demo@example.com')
    await page.fill('input[type="password"]', 'password')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard', { timeout: 10000 })
    
    // Click upgrade button from trial banner
    const upgradeButton = page.getByRole('button', { name: /View Plans|Upgrade/i }).first()
    await expect(upgradeButton).toBeVisible()
    await upgradeButton.click()
    
    // Should navigate to pricing page
    await page.waitForLoadState('domcontentloaded')
    await expect(page).toHaveURL(/.*\/pricing/)
    
    console.log('✅ Upgrade buttons from trial banner work correctly')
  })
  
  test('should display trial info correctly in trial-info page', async ({ page }) => {
    await page.goto('http://localhost:3000/trial-info', { waitUntil: 'domcontentloaded' })
    
    // Check all 3-day trial specific content
    await expect(page.getByText('3 Days Full Access')).toBeVisible()
    await expect(page.getByText('Start your free 3-day trial today')).toBeVisible()
    await expect(page.getByText('No credit card required • 3-day free trial • Cancel anytime')).toBeVisible()
    
    // Check that the start trial button works
    const startTrialButton = page.getByRole('button', { name: /Start.*Trial/i })
    await expect(startTrialButton).toBeVisible()
    await startTrialButton.click()
    
    // Should navigate to registration
    await page.waitForLoadState('domcontentloaded')
    await expect(page).toHaveURL(/.*\/auth\/register/)
    
    console.log('✅ Trial info page displays 3-day trial correctly')
  })
})


