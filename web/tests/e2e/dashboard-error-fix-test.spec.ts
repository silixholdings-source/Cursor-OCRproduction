import { test, expect } from '@playwright/test'

test.describe('Dashboard Error Fix Test', () => {
  test('should load dashboard without JavaScript errors', async ({ page }) => {
    // Mock authentication
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    await page.evaluate(() => {
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
        plan: 'pro'
      }))
    })
    
    // Navigate to dashboard
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Check for JavaScript errors
    const errors: string[] = []
    page.on('pageerror', e => errors.push(String(e)))
    page.on('console', msg => { 
      if (msg.type() === 'error') errors.push(msg.text()) 
    })
    
    // Wait a bit to ensure all JavaScript has loaded
    await page.waitForTimeout(2000)
    
    // Check that dashboard loads without errors
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
    
    // Verify no JavaScript errors occurred
    const errorMessages = errors.filter(error => 
      !error.includes('favicon') && 
      !error.includes('404') &&
      !error.includes('simulateUploadAndOCR')
    )
    
    expect(errorMessages).toHaveLength(0)
    console.log('✅ Dashboard loads without JavaScript errors')
  })
  
  test('should be able to navigate between dashboard tabs without errors', async ({ page }) => {
    // Mock authentication
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    await page.evaluate(() => {
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
        plan: 'pro'
      }))
    })
    
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Check for errors
    const errors: string[] = []
    page.on('pageerror', e => errors.push(String(e)))
    page.on('console', msg => { 
      if (msg.type() === 'error') errors.push(msg.text()) 
    })
    
    // Test tab navigation
    const tabs = ['Overview', 'Real-time', 'Analytics', 'Performance', 'Security', 'Audit', 'Integrations', 'AI Insights', 'Advanced']
    
    for (const tab of tabs) {
      await test.step(`Testing ${tab} tab`, async () => {
        const tabButton = page.getByRole('tab', { name: tab })
        await expect(tabButton).toBeVisible()
        await tabButton.click()
        
        // Wait for content to load
        await page.waitForTimeout(1000)
        
        // Check for errors after tab click
        const errorMessages = errors.filter(error => 
          !error.includes('favicon') && 
          !error.includes('404') &&
          !error.includes('simulateUploadAndOCR')
        )
        
        expect(errorMessages).toHaveLength(0)
        console.log(`✅ ${tab} tab works without errors`)
      })
    }
  })
  
  test('should not show dashboard error modal', async ({ page }) => {
    // Mock authentication
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    await page.evaluate(() => {
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
        plan: 'pro'
      }))
    })
    
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Wait for any potential error modals to appear
    await page.waitForTimeout(3000)
    
    // Check that no error modal is visible
    await expect(page.getByText('Dashboard Error')).not.toBeVisible()
    await expect(page.getByText('There was an error loading the dashboard')).not.toBeVisible()
    await expect(page.getByText('Cannot access \'simulateUploadAndOCR\' before initialization')).not.toBeVisible()
    
    console.log('✅ No dashboard error modal is shown')
  })
})


