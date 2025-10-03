import { test, expect } from '@playwright/test'

test.describe('Authenticated Navigation Test', () => {
  test('should show user info and sign out button when authenticated', async ({ page }) => {
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
    
    // Check that Sign In and Start Free Trial buttons are not visible
    await expect(page.getByRole('button', { name: 'Sign In' })).not.toBeVisible()
    await expect(page.getByRole('button', { name: 'Start Free Trial' })).not.toBeVisible()
    
    // Check that Dashboard link and user info are visible
    await expect(page.getByRole('link', { name: 'Dashboard' })).toBeVisible()
    await expect(page.getByText('Test User')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Sign Out' })).toBeVisible()
    
    console.log('✅ Authenticated navigation is working correctly')
  })
  
  test('should show sign in and start free trial buttons when not authenticated', async ({ page }) => {
    // Clear authentication data
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    await page.evaluate(() => {
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_company')
    })
    
    // Reload the page
    await page.reload({ waitUntil: 'domcontentloaded' })
    
    // Check that Sign In and Start Free Trial buttons are visible
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Start Free Trial' })).toBeVisible()
    
    // Check that Dashboard link and user info are not visible
    await expect(page.getByRole('link', { name: 'Dashboard' })).not.toBeVisible()
    await expect(page.getByText('Test User')).not.toBeVisible()
    await expect(page.getByRole('button', { name: 'Sign Out' })).not.toBeVisible()
    
    console.log('✅ Unauthenticated navigation is working correctly')
  })
  
  test('should redirect to login when accessing dashboard without authentication', async ({ page }) => {
    // Clear authentication data
    await page.evaluate(() => {
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_company')
    })
    
    // Try to access dashboard
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Should be redirected to login page
    await expect(page).toHaveURL(/.*\/auth\/login/)
    
    console.log('✅ Dashboard redirect to login is working correctly')
  })
})


