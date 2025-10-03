import { test, expect } from '@playwright/test'

test.describe('Anchor Tag Test', () => {
  test('test if regular anchor tags work', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    
    // Inject a simple anchor tag to test navigation
    await page.evaluate(() => {
      const testAnchor = document.createElement('a')
      testAnchor.href = '/auth/register'
      testAnchor.textContent = 'Test Link'
      testAnchor.style.position = 'fixed'
      testAnchor.style.top = '10px'
      testAnchor.style.right = '10px'
      testAnchor.style.background = 'red'
      testAnchor.style.color = 'white'
      testAnchor.style.padding = '10px'
      testAnchor.style.zIndex = '9999'
      document.body.appendChild(testAnchor)
    })
    
    // Wait a bit for the anchor to be added
    await page.waitForTimeout(1000)
    
    // Click the test anchor
    await page.click('a[href="/auth/register"]:has-text("Test Link")')
    await page.waitForTimeout(2000)
    
    console.log(`URL after clicking test anchor: ${page.url()}`)
    
    if (page.url().includes('/auth/register')) {
      console.log('✅ Regular anchor tag navigation works')
    } else {
      console.log('❌ Regular anchor tag navigation failed')
    }
  })
})


