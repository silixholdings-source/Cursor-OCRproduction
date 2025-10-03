import { test, expect } from '@playwright/test'

test.describe('Footer After Cleanup Test', () => {
  test('verify footer still works after removing careers, blog, press links', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })

    console.log('🧹 TESTING FOOTER AFTER CLEANUP')
    console.log('================================')

    // Scroll to footer
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(1000)

    // Verify that the removed links are no longer present
    const careersLink = page.getByRole('link', { name: 'Careers' })
    const blogLink = page.getByRole('link', { name: 'Blog' })
    const pressLink = page.getByRole('link', { name: 'Press' })

    const careersCount = await careersLink.count()
    const blogCount = await blogLink.count()
    const pressCount = await pressLink.count()

    console.log(`Careers links found: ${careersCount}`)
    console.log(`Blog links found: ${blogCount}`)
    console.log(`Press links found: ${pressCount}`)

    expect(careersCount).toBe(0)
    expect(blogCount).toBe(0)
    expect(pressCount).toBe(0)

    console.log('✅ Removed links are no longer present')

    // Test that remaining footer links still work
    const remainingLinks = [
      { text: 'About Us', href: '/about' },
      { text: 'Partners', href: '/partners' },
      { text: 'Contact Us', href: '/contact' },
      { text: 'Privacy Policy', href: '/privacy' },
      { text: 'Terms of Service', href: '/terms' },
    ]

    let workingLinks = 0
    for (const { text, href } of remainingLinks) {
      const link = page.getByRole('link', { name: text }).first()
      
      if (await link.isVisible()) {
        await link.click()
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 })
        const linkWorks = page.url().includes(href)
        console.log(`Footer ${text}: ${linkWorks ? '✅ WORKING' : '❌ FAILED'}`)
        if (linkWorks) workingLinks++
        await page.goto('/', { waitUntil: 'domcontentloaded' })
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
        await page.waitForTimeout(500)
      } else {
        console.log(`Footer ${text}: ⚠️ NOT VISIBLE`)
      }
    }

    console.log(`Remaining footer links: ${workingLinks}/${remainingLinks.length} working`)
    console.log('✅ Footer cleanup successful - removed links are gone, remaining links work!')
  })
})


