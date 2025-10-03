import { test, expect } from '@playwright/test'

test.describe('ROI Calculator Button Test', () => {
  test('should navigate to registration when Start Your Free Trial button is clicked', async ({ page }) => {
    // Navigate to the ROI calculator page
    await page.goto('http://localhost:3000/roi-calculator', { waitUntil: 'domcontentloaded' })
    
    // Check that the ROI calculator page loads
    await expect(page.getByText('ROI Calculator')).toBeVisible()
    
    // Find and click the "Start Your Free Trial" button
    const startTrialButton = page.getByRole('button', { name: 'Start Your Free Trial' })
    await expect(startTrialButton).toBeVisible()
    await startTrialButton.click()
    
    // Verify navigation to registration page
    await expect(page).toHaveURL(/.*\/auth\/register/)
    
    console.log('✅ ROI Calculator "Start Your Free Trial" button works correctly')
  })
  
  test('should show ROI summary and working button', async ({ page }) => {
    await page.goto('http://localhost:3000/roi-calculator', { waitUntil: 'domcontentloaded' })
    
    // Check that ROI summary is visible
    await expect(page.getByText('Your ROI Summary')).toBeVisible()
    
    // Check that the button is visible and clickable
    const startTrialButton = page.getByRole('button', { name: 'Start Your Free Trial' })
    await expect(startTrialButton).toBeVisible()
    await expect(startTrialButton).toBeEnabled()
    
    // Check that the button has the correct styling
    await expect(startTrialButton).toHaveClass(/bg-green-600/)
    
    // Check that the button has an arrow icon
    const arrowIcon = startTrialButton.locator('svg')
    await expect(arrowIcon).toBeVisible()
    
    console.log('✅ ROI Calculator button is properly styled and functional')
  })
  
  test('should show trial information below button', async ({ page }) => {
    await page.goto('http://localhost:3000/roi-calculator', { waitUntil: 'domcontentloaded' })
    
    // Check that trial information is displayed
    await expect(page.getByText('No credit card required • 14-day free trial')).toBeVisible()
    
    console.log('✅ Trial information is displayed correctly')
  })
})


