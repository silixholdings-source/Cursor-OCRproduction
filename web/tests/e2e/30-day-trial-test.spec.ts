import { test, expect } from '@playwright/test'

test.describe('30-Day Trial Period Test', () => {
  test('should display 30-day trial period on homepage', async ({ page }) => {
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    // Check for 30-day trial mentions on homepage
    await expect(page.getByText('30-day free trial')).toBeVisible()
    await expect(page.getByText('No credit card required • 30-day free trial • Setup in 5 minutes')).toBeVisible()
    
    // Should not find any 14-day trial mentions
    await expect(page.getByText('14-day free trial')).not.toBeVisible()
    
    console.log('✅ Homepage shows 30-day trial period')
  })
  
  test('should display 30-day trial in ROI Calculator', async ({ page }) => {
    await page.goto('http://localhost:3000/roi-calculator', { waitUntil: 'domcontentloaded' })
    
    // Check ROI Calculator trial period
    await expect(page.getByText('No credit card required • 30-day free trial')).toBeVisible()
    
    console.log('✅ ROI Calculator shows 30-day trial period')
  })
  
  test('should display 30-day trial in pricing page', async ({ page }) => {
    await page.goto('http://localhost:3000/pricing', { waitUntil: 'domcontentloaded' })
    
    // Check pricing page trial mentions
    await expect(page.getByText('30-day free trial')).toBeVisible()
    await expect(page.getByText('Start with a 30-day free trial for all plans')).toBeVisible()
    
    console.log('✅ Pricing page shows 30-day trial period')
  })
  
  test('should display 30-day trial in trial info page', async ({ page }) => {
    await page.goto('http://localhost:3000/trial-info', { waitUntil: 'domcontentloaded' })
    
    // Check trial info page
    await expect(page.getByText('30 Days Full Access')).toBeVisible()
    await expect(page.getByText('Start your free 30-day trial today')).toBeVisible()
    await expect(page.getByText('No credit card required • 30-day free trial • Cancel anytime')).toBeVisible()
    
    console.log('✅ Trial info page shows 30-day trial period')
  })
  
  test('should display 30-day trial in registration page', async ({ page }) => {
    await page.goto('http://localhost:3000/auth/register?trial=true', { waitUntil: 'domcontentloaded' })
    
    // Check registration page for trial users
    await expect(page.getByText('Start Your Free 30-Day Trial')).toBeVisible()
    await expect(page.getByText('You\'re starting a 30-day free trial with full access')).toBeVisible()
    
    console.log('✅ Registration page shows 30-day trial period')
  })
  
  test('should display 30-day trial for all pricing plans', async ({ page }) => {
    await page.goto('http://localhost:3000/pricing', { waitUntil: 'domcontentloaded' })
    
    // Check that all pricing plan buttons show 30-day trial
    const trialButtons = page.getByText(/Start 30-day free trial/i)
    const buttonCount = await trialButtons.count()
    
    // Should have multiple pricing plan buttons
    expect(buttonCount).toBeGreaterThan(0)
    
    // Check specific pricing plans
    await expect(page.getByRole('button', { name: /Start 30-day free trial/i })).toBeVisible()
    
    console.log(`✅ Found ${buttonCount} pricing plan buttons with 30-day trial`)
  })
  
  test('should not display any 14-day trial references', async ({ page }) => {
    const pagesToCheck = [
      'http://localhost:3000',
      'http://localhost:3000/pricing',
      'http://localhost:3000/roi-calculator',
      'http://localhost:3000/trial-info',
      'http://localhost:3000/features'
    ]
    
    for (const pageUrl of pagesToCheck) {
      await page.goto(pageUrl, { waitUntil: 'domcontentloaded' })
      
      // Should not find any 14-day trial mentions
      const oldTrialText = page.getByText('14-day')
      const count = await oldTrialText.count()
      
      expect(count).toBe(0)
      console.log(`✅ ${pageUrl} has no 14-day trial references`)
    }
  })
})


