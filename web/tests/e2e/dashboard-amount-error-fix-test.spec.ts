import { test, expect } from '@playwright/test'

test.describe('Dashboard Amount Error Fix Test', () => {
  test('should not show "toFixed is not a function" error', async ({ page }) => {
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
    
    // Wait for dashboard to fully load
    await page.waitForTimeout(3000)
    
    // Check that dashboard loads without errors
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
    
    // Verify no "toFixed" errors occurred
    const toFixedErrors = errors.filter(error => 
      error.includes('toFixed is not a function') ||
      error.includes('extractedData.amount.toFixed')
    )
    
    expect(toFixedErrors).toHaveLength(0)
    console.log('✅ No "toFixed is not a function" errors occurred')
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
    await expect(page.getByText('extractedData.amount.toFixed is not a function')).not.toBeVisible()
    
    console.log('✅ No dashboard error modal is shown')
  })
  
  test('should display dashboard stats correctly', async ({ page }) => {
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
    
    // Check that dashboard stats are visible and properly formatted
    await expect(page.getByText('Total Invoices')).toBeVisible()
    await expect(page.getByText('Processed Today')).toBeVisible()
    await expect(page.getByText('Pending Approval')).toBeVisible()
    await expect(page.getByText('Total Amount')).toBeVisible()
    await expect(page.getByText('Success Rate')).toBeVisible()
    await expect(page.getByText('Avg Processing Time')).toBeVisible()
    await expect(page.getByText('Active Users')).toBeVisible()
    await expect(page.getByText('System Health')).toBeVisible()
    
    console.log('✅ Dashboard stats are displayed correctly')
  })
})


