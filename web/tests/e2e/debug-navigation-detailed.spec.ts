import { test, expect } from '@playwright/test'

test.describe('Debug Navigation Detailed', () => {
  test('debug navigation issues', async ({ page }) => {
    // Listen for console errors
    const errors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })

    // Listen for page errors
    page.on('pageerror', error => {
      errors.push(error.message)
    })

    await page.goto('/', { waitUntil: 'domcontentloaded' })

    console.log('=== DEBUGGING NAVIGATION ===')

    // Check all buttons and their properties
    const allButtons = page.locator('button')
    const buttonCount = await allButtons.count()
    console.log(`Total buttons: ${buttonCount}`)

    for (let i = 0; i < buttonCount; i++) {
      const button = allButtons.nth(i)
      const text = await button.textContent()
      const tagName = await button.evaluate(el => el.tagName)
      const className = await button.getAttribute('class')
      const onClick = await button.evaluate(el => el.onclick?.toString() || 'none')
      
      console.log(`Button ${i}: "${text}" (${tagName}) - onClick: ${onClick}`)
      
      if (text?.includes('Start Free Trial')) {
        console.log(`Found Start Free Trial button at index ${i}`)
        
        // Try to click and see what happens
        console.log('Clicking button...')
        await button.click()
        await page.waitForTimeout(2000)
        console.log(`URL after click: ${page.url()}`)
        
        // Check for any errors
        if (errors.length > 0) {
          console.log('Errors found:', errors)
        }
        
        // Go back to home
        await page.goto('/', { waitUntil: 'domcontentloaded' })
        break
      }
    }

    // Also check all links
    const allLinks = page.locator('a')
    const linkCount = await allLinks.count()
    console.log(`Total links: ${linkCount}`)

    for (let i = 0; i < Math.min(linkCount, 10); i++) {
      const link = allLinks.nth(i)
      const text = await link.textContent()
      const href = await link.getAttribute('href')
      
      if (text?.includes('Start Free Trial')) {
        console.log(`Found Start Free Trial link: "${text}" -> ${href}`)
      }
    }

    // Test the LinkButton component specifically
    console.log('Testing LinkButton components...')
    const linkButtons = page.locator('a[class*="bg-white"][class*="text-blue-600"]')
    const linkButtonCount = await linkButtons.count()
    console.log(`LinkButton components found: ${linkButtonCount}`)

    if (linkButtonCount > 0) {
      const firstLinkButton = linkButtons.first()
      const text = await firstLinkButton.textContent()
      const href = await firstLinkButton.getAttribute('href')
      console.log(`First LinkButton: "${text}" -> ${href}`)
      
      console.log('Clicking LinkButton...')
      await firstLinkButton.click()
      await page.waitForTimeout(2000)
      console.log(`URL after LinkButton click: ${page.url()}`)
    }

    console.log('=== END DEBUG ===')
  })
})


