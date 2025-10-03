import { test, expect } from '@playwright/test'

test.describe('New Navigation Pages Test', () => {
  const pagesToTest = [
    { path: '/integrations', title: 'Integrations' },
    { path: '/security', title: 'Security' },
    { path: '/support', title: 'Support Center' },
  ]

  test('test the new navigation pages', async ({ page }) => {
    for (const { path, title } of pagesToTest) {
      await test.step(`Test page: ${path}`, async () => {
        const response = await page.goto(`http://localhost:3000${path}`, { waitUntil: 'domcontentloaded' })
        
        console.log(`${title} (${path}): Status ${response?.status()}, URL: ${page.url()}`)

        expect(response?.ok()).toBeTruthy()
        expect(page.url()).toContain(path)
        await expect(page.getByRole('heading', { name: title, level: 1 })).toBeVisible()
        console.log(`✅ ${title} is now working (Status: ${response?.status()})`)
        console.log(`   Page title: "${await page.title()}"`)
      })
    }
  })
})
