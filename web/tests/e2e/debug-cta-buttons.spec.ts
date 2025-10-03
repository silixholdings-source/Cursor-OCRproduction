import { test, expect } from '@playwright/test'

test.describe('Debug CTA Buttons', () => {
  test('debug CTA button behavior', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })

    // Log all buttons on the page
    const allButtons = page.locator('button')
    const totalButtons = await allButtons.count()
    console.log(`Total buttons found: ${totalButtons}`)

    // Log all links on the page
    const allLinks = page.locator('a')
    const totalLinks = await allLinks.count()
    console.log(`Total links found: ${totalLinks}`)

    // Find Start Free Trial buttons
    const trialButtons = page.getByRole('button', { name: /Start Free Trial/i })
    const trialCount = await trialButtons.count()
    console.log(`Start Free Trial buttons found: ${trialCount}`)

    if (trialCount > 0) {
      // Get the first button and inspect it
      const firstButton = trialButtons.first()
      const buttonText = await firstButton.textContent()
      const buttonHTML = await firstButton.innerHTML()
      const buttonTagName = await firstButton.evaluate(el => el.tagName)
      const buttonHref = await firstButton.getAttribute('href')
      
      console.log(`First button text: "${buttonText}"`)
      console.log(`First button HTML: ${buttonHTML}`)
      console.log(`First button tag: ${buttonTagName}`)
      console.log(`First button href: ${buttonHref}`)

      // Check if it's actually a link
      const parentLink = firstButton.locator('xpath=..').filter('a')
      const parentLinkCount = await parentLink.count()
      console.log(`Parent link count: ${parentLinkCount}`)

      if (parentLinkCount > 0) {
        const parentHref = await parentLink.first().getAttribute('href')
        console.log(`Parent link href: ${parentHref}`)
      }

      // Try clicking and see what happens
      console.log('Clicking Start Free Trial button...')
      await firstButton.click()
      await page.waitForTimeout(2000)
      console.log(`URL after click: ${page.url()}`)

      // Check for any console errors
      page.on('console', msg => {
        if (msg.type() === 'error') {
          console.log(`Console error: ${msg.text()}`)
        }
      })
    }

    // Also check for links with "Start Free Trial" text
    const trialLinks = page.getByRole('link', { name: /Start Free Trial/i })
    const trialLinkCount = await trialLinks.count()
    console.log(`Start Free Trial links found: ${trialLinkCount}`)

    if (trialLinkCount > 0) {
      const firstLink = trialLinks.first()
      const linkHref = await firstLink.getAttribute('href')
      console.log(`First trial link href: ${linkHref}`)
    }

    // Take a screenshot for debugging
    await page.screenshot({ path: 'debug-cta-buttons.png', fullPage: true })
  })
})


