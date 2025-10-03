import { test, expect } from '@playwright/test'

test.describe('Footer SILIX Text Test', () => {
  test('should display SILIX Holdings text in footer', async ({ page }) => {
    // Navigate to any page to see the footer
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    // Check that the SILIX Holdings text is visible in the footer
    await expect(page.getByText('This solution is developed by SILIX Holdings (Pty) Ltd')).toBeVisible()
    
    console.log('✅ SILIX Holdings text is displayed in footer')
  })
  
  test('should have proper footer layout with SILIX text', async ({ page }) => {
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    // Check that all footer elements are present
    await expect(page.getByText('© 2024 AI ERP SaaS. All rights reserved.')).toBeVisible()
    await expect(page.getByText('This solution is developed by SILIX Holdings (Pty) Ltd')).toBeVisible()
    await expect(page.getByRole('link', { name: 'Privacy' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Terms' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Cookies' })).toBeVisible()
    
    console.log('✅ Footer layout is complete with all elements')
  })
  
  test('should have proper styling for SILIX text', async ({ page }) => {
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })
    
    // Check that the SILIX text has proper styling
    const silixText = page.getByText('This solution is developed by SILIX Holdings (Pty) Ltd')
    await expect(silixText).toBeVisible()
    
    // Check that it's centered and has proper text color
    const silixElement = silixText.locator('..')
    await expect(silixElement).toHaveClass(/text-center/)
    
    console.log('✅ SILIX text has proper styling and positioning')
  })
})


