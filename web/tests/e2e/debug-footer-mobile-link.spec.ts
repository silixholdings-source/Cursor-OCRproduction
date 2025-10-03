import { test, expect } from '@playwright/test'

test.describe('Debug Footer Mobile Link', () => {
  test('debug footer mobile link issue', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })

    console.log('=== DEBUGGING FOOTER MOBILE LINK ===')

    // Scroll to footer
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(1000)

    // Find all links with "Mobile" in them
    const mobileLinks = page.getByRole('link', { name: /Mobile/i })
    const mobileLinkCount = await mobileLinks.count()
    console.log(`Found ${mobileLinkCount} links with "Mobile" in the name`)

    // Check all links in the footer
    const allFooterLinks = page.locator('footer a')
    const footerLinkCount = await allFooterLinks.count()
    console.log(`Found ${footerLinkCount} links in footer`)

    for (let i = 0; i < Math.min(footerLinkCount, 10); i++) {
      const link = allFooterLinks.nth(i)
      const text = await link.textContent()
      const href = await link.getAttribute('href')
      console.log(`Footer link ${i}: "${text}" -> ${href}`)
    }

    // Try to find the specific mobile link
    const mobileLink = page.getByRole('link', { name: 'Mobile Apps' }).first()
    if (await mobileLink.isVisible()) {
      const href = await mobileLink.getAttribute('href')
      console.log(`Mobile Apps link href: ${href}`)
      
      console.log('Clicking Mobile Apps link...')
      await mobileLink.click()
      await page.waitForTimeout(2000)
      console.log(`URL after click: ${page.url()}`)
    } else {
      console.log('Mobile Apps link not visible')
    }

    console.log('=== END DEBUG ===')
  })
})


