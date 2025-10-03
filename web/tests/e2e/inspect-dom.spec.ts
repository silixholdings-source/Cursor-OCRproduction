import { test, expect } from '@playwright/test'

test.describe('DOM Inspection', () => {
  test('inspect actual DOM structure of CTA buttons', async ({ page }) => {
    await page.setViewportSize({ width: 1200, height: 800 })
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(3000)
    
    // Find all Start Free Trial elements
    const startFreeTrialElements = page.locator('text=Start Free Trial')
    const count = await startFreeTrialElements.count()
    console.log(`Start Free Trial text elements found: ${count}`)
    
    for (let i = 0; i < count; i++) {
      const element = startFreeTrialElements.nth(i)
      const tagName = await element.evaluate(el => el.tagName)
      const parentTagName = await element.evaluate(el => el.parentElement?.tagName)
      const grandParentTagName = await element.evaluate(el => el.parentElement?.parentElement?.tagName)
      
      console.log(`Element ${i}:`)
      console.log(`  Text element: ${tagName}`)
      console.log(`  Parent: ${parentTagName}`)
      console.log(`  Grandparent: ${grandParentTagName}`)
      
      // Check if any parent is a link
      const isInLink = await element.evaluate(el => {
        let current = el
        while (current && current.tagName !== 'BODY') {
          if (current.tagName === 'A') {
            return { isLink: true, href: current.getAttribute('href'), tagName: current.tagName }
          }
          current = current.parentElement
        }
        return { isLink: false }
      })
      
      console.log(`  In link: ${JSON.stringify(isInLink)}`)
      
      // Get the clickable element (the one with button-like classes)
      const clickableParent = element.locator('xpath=ancestor::*[contains(@class, "inline-flex") or contains(@class, "button") or contains(@class, "bg-white")]').first()
      if (await clickableParent.count() > 0) {
        const clickableTagName = await clickableParent.evaluate(el => el.tagName)
        const clickableHref = await clickableParent.getAttribute('href')
        const clickableClasses = await clickableParent.getAttribute('class')
        console.log(`  Clickable element: ${clickableTagName}`)
        console.log(`  Clickable href: ${clickableHref}`)
        console.log(`  Clickable classes: ${clickableClasses}`)
      }
      
      console.log('---')
    }
    
    // Also check for any links with href="/auth/register"
    const authRegisterLinks = page.locator('a[href="/auth/register"]')
    const linkCount = await authRegisterLinks.count()
    console.log(`Direct auth/register links found: ${linkCount}`)
    
    for (let i = 0; i < linkCount; i++) {
      const link = authRegisterLinks.nth(i)
      const linkText = await link.textContent()
      const linkClasses = await link.getAttribute('class')
      console.log(`Link ${i}: "${linkText}" - classes: ${linkClasses}`)
    }
  })
})


