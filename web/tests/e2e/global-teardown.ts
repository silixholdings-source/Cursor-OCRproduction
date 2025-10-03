import { FullConfig } from '@playwright/test'

async function globalTeardown(config: FullConfig) {
  // Clean up any resources created during tests
  // For now, we'll just log completion
  
  console.log('Global teardown completed')
}

export default globalTeardown
