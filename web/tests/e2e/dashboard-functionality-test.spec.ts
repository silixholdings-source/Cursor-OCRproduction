import { test, expect } from '@playwright/test'

test.describe('Dashboard Functionality Test', () => {
  test('should be able to navigate between all dashboard tabs', async ({ page }) => {
    // Navigate to dashboard (assuming user is logged in)
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Check that dashboard loads
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
    
    // Test each tab
    const tabs = [
      { name: 'Overview', id: 'overview' },
      { name: 'Real-time', id: 'realtime' },
      { name: 'Analytics', id: 'analytics' },
      { name: 'Performance', id: 'performance' },
      { name: 'Security', id: 'security' },
      { name: 'Audit', id: 'audit' },
      { name: 'Integrations', id: 'integrations' },
      { name: 'AI Insights', id: 'ai' },
      { name: 'Advanced', id: 'advanced' }
    ]
    
    for (const tab of tabs) {
      await test.step(`Testing ${tab.name} tab`, async () => {
        // Click on the tab
        const tabButton = page.getByRole('tab', { name: tab.name })
        await expect(tabButton).toBeVisible()
        await tabButton.click()
        
        // Wait for content to load
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
        
        // Verify the tab is active
        await expect(tabButton).toHaveAttribute('data-state', 'active')
        
        // Check that some content is visible (not just empty)
        const content = page.locator('[data-state="active"]').first()
        await expect(content).toBeVisible()
        
        console.log(`✅ ${tab.name} tab is working`)
      })
    }
  })
  
  test('should have working quick action buttons', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Check that quick actions are visible
    await expect(page.getByText('Quick Actions')).toBeVisible()
    
    // Test quick action buttons
    const quickActions = [
      'Process Invoice',
      'Approve Pending', 
      'View Reports',
      'ERP Settings'
    ]
    
    for (const action of quickActions) {
      const button = page.getByRole('button', { name: action })
      await expect(button).toBeVisible()
      console.log(`✅ Quick action "${action}" is visible`)
    }
  })
  
  test('should display dashboard stats correctly', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'domcontentloaded' })
    
    // Check that stats are visible
    const stats = [
      'Total Invoices',
      'Processed Today',
      'Pending Approval',
      'Total Amount',
      'Success Rate',
      'Avg Processing Time',
      'Active Users',
      'System Health'
    ]
    
    for (const stat of stats) {
      await expect(page.getByText(stat)).toBeVisible()
      console.log(`✅ Stat "${stat}" is visible`)
    }
  })
})


