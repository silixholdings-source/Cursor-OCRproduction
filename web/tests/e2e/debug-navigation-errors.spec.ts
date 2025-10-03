import { test, expect } from '@playwright/test'

test.describe('Debug Navigation Errors', () => {
  test('debug navigation button errors', async ({ page }) => {
    // Listen for console errors
    const errors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
        console.log(`Console error: ${msg.text()}`)
      }
    })

    // Listen for page errors
    page.on('pageerror', error => {
      errors.push(error.message)
      console.log(`Page error: ${error.message}`)
    })

    await page.goto('/', { waitUntil: 'domcontentloaded' })

    console.log('=== DEBUGGING NAVIGATION ERRORS ===')

    // Check if router is available
    const routerCheck = await page.evaluate(() => {
      // Check if Next.js router is available
      const hasRouter = typeof window !== 'undefined' && window.next
      return {
        hasRouter,
        userAgent: navigator.userAgent,
        location: window.location.href
      }
    })
    console.log('Router check:', routerCheck)

    // Test button click with error monitoring
    const signInButton = page.getByRole('button', { name: /Sign In/i }).first()
    if (await signInButton.isVisible()) {
      console.log('Clicking Sign In button...')
      await signInButton.click()
      await page.waitForTimeout(3000)
      console.log(`URL after click: ${page.url()}`)
      console.log(`Errors after click: ${errors.length}`)
      
      if (errors.length > 0) {
        console.log('All errors:', errors)
      }
    }

    // Check if there are any JavaScript errors in the page
    const jsErrors = await page.evaluate(() => {
      const errors = []
      window.addEventListener('error', (e) => {
        errors.push(e.message)
      })
      return errors
    })
    console.log('JavaScript errors:', jsErrors)

    console.log('=== END DEBUG ===')
  })
})


