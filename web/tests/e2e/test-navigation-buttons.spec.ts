import { test, expect } from '@playwright/test'

test.describe('Navigation Component Buttons', () => {
  test('test Navigation component buttons', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })

    console.log('=== TESTING NAVIGATION COMPONENT BUTTONS ===')

    // Test Sign In button in Navigation component
    const signInButtons = page.getByRole('button', { name: /Sign In/i })
    const signInCount = await signInButtons.count()
    console.log(`Sign In buttons found: ${signInCount}`)

    if (signInCount > 0) {
      console.log('Clicking Sign In button...')
      await signInButtons.first().click()
      await page.waitForTimeout(2000)
      console.log(`URL after Sign In click: ${page.url()}`)
      
      if (page.url().includes('/auth/login')) {
        console.log('✅ Sign In button works!')
      } else {
        console.log('❌ Sign In button failed to navigate')
      }
      
      // Go back to home
      await page.goto('/', { waitUntil: 'domcontentloaded' })
    }

    // Test Start Free Trial button in Navigation component
    const startTrialButtons = page.getByRole('button', { name: /Start Free Trial/i })
    const trialCount = await startTrialButtons.count()
    console.log(`Start Free Trial buttons found: ${trialCount}`)

    if (trialCount > 0) {
      console.log('Clicking Start Free Trial button...')
      await startTrialButtons.first().click()
      await page.waitForTimeout(2000)
      console.log(`URL after Start Free Trial click: ${page.url()}`)
      
      if (page.url().includes('/auth/register')) {
        console.log('✅ Start Free Trial button works!')
      } else {
        console.log('❌ Start Free Trial button failed to navigate')
      }
    }

    console.log('=== END TEST ===')
  })
})


