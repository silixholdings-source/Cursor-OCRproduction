import { test, expect } from '@playwright/test'

test.describe('Authenticated App Functionality Test', () => {
  test('should show all app functionality links when user is authenticated', async ({ page }) => {
    // Mock authentication by setting localStorage
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    // Set mock authentication data
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
    
    // Reload the page to trigger authentication
    await page.reload({ waitUntil: 'domcontentloaded' })
    
    // Check that all app functionality links are visible for authenticated users
    const appLinks = [
      'Dashboard',
      'Invoices', 
      'Approvals',
      'Vendors',
      'Analytics',
      'Settings',
      'Support'
    ]
    
    for (const link of appLinks) {
      await expect(page.getByRole('link', { name: link })).toBeVisible()
      console.log(`✅ App functionality link "${link}" is visible for authenticated user`)
    }
    
    // Check that marketing links are NOT visible for authenticated users
    const marketingLinks = ['Features', 'Pricing', 'Integrations', 'Security', 'Contact Us']
    
    for (const link of marketingLinks) {
      await expect(page.getByRole('link', { name: link })).not.toBeVisible()
      console.log(`✅ Marketing link "${link}" is hidden for authenticated user`)
    }
    
    // Check that user info and sign out are visible
    await expect(page.getByText('Test User')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Sign Out' })).toBeVisible()
    
    console.log('✅ All app functionality is properly accessible for authenticated users')
  })
  
  test('should show marketing links when user is not authenticated', async ({ page }) => {
    // Clear authentication data
    await page.evaluate(() => {
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_company')
    })
    
    // Reload the page
    await page.reload({ waitUntil: 'domcontentloaded' })
    
    // Check that marketing links are visible for unauthenticated users
    const marketingLinks = ['Features', 'Pricing', 'Integrations', 'Security', 'Support', 'Contact Us']
    
    for (const link of marketingLinks) {
      await expect(page.getByRole('link', { name: link })).toBeVisible()
      console.log(`✅ Marketing link "${link}" is visible for unauthenticated user`)
    }
    
    // Check that app functionality links are NOT visible for unauthenticated users
    const appLinks = ['Dashboard', 'Invoices', 'Approvals', 'Vendors', 'Analytics', 'Settings']
    
    for (const link of appLinks) {
      await expect(page.getByRole('link', { name: link })).not.toBeVisible()
      console.log(`✅ App functionality link "${link}" is hidden for unauthenticated user`)
    }
    
    // Check that sign in and start free trial buttons are visible
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Start Free Trial' })).toBeVisible()
    
    console.log('✅ Marketing links are properly shown for unauthenticated users')
  })
  
  test('should be able to navigate to all app functionality pages when authenticated', async ({ page }) => {
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
    
    await page.reload({ waitUntil: 'domcontentloaded' })
    
    // Test navigation to each app functionality page
    const appPages = [
      { name: 'Dashboard', url: '/dashboard' },
      { name: 'Invoices', url: '/dashboard/invoices' },
      { name: 'Approvals', url: '/dashboard/approvals' },
      { name: 'Vendors', url: '/dashboard/vendors' },
      { name: 'Analytics', url: '/dashboard/analytics' },
      { name: 'Settings', url: '/dashboard/settings' }
    ]
    
    for (const pageInfo of appPages) {
      await test.step(`Testing navigation to ${pageInfo.name}`, async () => {
        // Click on the navigation link
        await page.getByRole('link', { name: pageInfo.name }).click()
        
        // Wait for navigation
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
        
        // Verify we're on the correct page
        await expect(page).toHaveURL(new RegExp(pageInfo.url))
        
        console.log(`✅ Successfully navigated to ${pageInfo.name}`)
      })
    }
  })
})


