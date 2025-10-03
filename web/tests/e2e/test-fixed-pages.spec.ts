import { test, expect } from '@playwright/test'

test.describe('Fixed Pages Test', () => {
  test('test the pages we just created', async ({ page }) => {
    const pagesToTest = [
      { route: '/privacy', name: 'Privacy Policy' },
      { route: '/terms', name: 'Terms of Service' },
      { route: '/cookies', name: 'Cookie Policy' },
      { route: '/partners', name: 'Partners' },
      { route: '/status', name: 'System Status' }
    ]
    
    for (const { route, name } of pagesToTest) {
      await test.step(`testing ${name} (${route})`, async () => {
        const response = await page.goto(route, { waitUntil: 'domcontentloaded' })
        
        if (response) {
          const status = response.status()
          const finalUrl = page.url()
          
          console.log(`${name} (${route}): Status ${status}, URL: ${finalUrl}`)
          
          if (status === 404) {
            console.log(`❌ ${name} still returns 404`)
          } else if (status >= 200 && status < 400) {
            console.log(`✅ ${name} is now working (Status: ${status})`)
            
            // Check if the page content is displayed
            const hasContent = await page.locator('h1').count() > 0
            if (hasContent) {
              const pageTitle = await page.locator('h1').first().textContent()
              console.log(`   Page title: "${pageTitle}"`)
            }
          } else {
            console.log(`⚠️ ${name} has unexpected status: ${status}`)
          }
        }
      })
    }
  })
})


