import { test, expect } from '@playwright/test'

test.describe('404 Route Testing', () => {
  test('test common routes that might cause 404 errors', async ({ page }) => {
    const routesToTest = [
      '/',
      '/features',
      '/pricing', 
      '/about',
      '/contact',
      '/demo',
      '/auth/login',
      '/auth/register',
      '/dashboard',
      '/signup',
      '/login',
      '/trial-info',
      '/test',
      '/api',
      '/docs',
      '/status',
      '/partners',
      '/privacy',
      '/terms',
      '/ccpa',
      '/gdpr',
      '/cookies'
    ]
    
    for (const route of routesToTest) {
      await test.step(`testing route: ${route}`, async () => {
        const response = await page.goto(route, { waitUntil: 'domcontentloaded' })
        
        if (response) {
          const status = response.status()
          const finalUrl = page.url()
          
          console.log(`Route ${route}: Status ${status}, Final URL: ${finalUrl}`)
          
          if (status === 404) {
            console.log(`❌ 404 Error on route: ${route}`)
          } else if (status >= 200 && status < 400) {
            console.log(`✅ Route ${route} works (Status: ${status})`)
          } else {
            console.log(`⚠️ Route ${route} has status: ${status}`)
          }
          
          // Check if we're on a 404 page
          const is404Page = await page.locator('text=Page not found').count() > 0
          if (is404Page) {
            console.log(`❌ 404 page detected for route: ${route}`)
          }
        }
      })
    }
  })
})


