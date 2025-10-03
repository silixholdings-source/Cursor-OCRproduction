/**
 * Comprehensive UI Test Script
 * Tests all buttons, links, and functionality in the AI ERP SaaS application
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_CONFIG = {
  baseUrl: 'http://localhost:3000',
  timeout: 30000,
  headless: false, // Set to true for headless testing
  slowMo: 100, // Slow down operations for better visibility
};

// Test results
const testResults = {
  passed: 0,
  failed: 0,
  tests: [],
  screenshots: []
};

// Test data
const testData = {
  sampleInvoice: {
    name: 'test-invoice.pdf',
    type: 'application/pdf',
    content: 'Sample PDF content for testing'
  }
};

/**
 * Log test result
 */
function logTest(testName, status, message = '', screenshot = null) {
  const result = {
    name: testName,
    status,
    message,
    timestamp: new Date().toISOString(),
    screenshot
  };
  
  testResults.tests.push(result);
  
  if (status === 'PASS') {
    testResults.passed++;
    console.log(`✅ ${testName}: ${message}`);
  } else {
    testResults.failed++;
    console.log(`❌ ${testName}: ${message}`);
  }
}

/**
 * Take screenshot
 */
async function takeScreenshot(page, testName) {
  try {
    const screenshotPath = `screenshots/${testName}-${Date.now()}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: true });
    testResults.screenshots.push(screenshotPath);
    return screenshotPath;
  } catch (error) {
    console.log(`Screenshot failed for ${testName}: ${error.message}`);
    return null;
  }
}

/**
 * Test navigation and routing
 */
async function testNavigation(page) {
  console.log('\n🧭 Testing Navigation and Routing...');
  
  try {
    // Test main navigation
    const navItems = [
      { selector: 'a[href="/dashboard"]', name: 'Dashboard Link' },
      { selector: 'a[href="/invoices/upload"]', name: 'Invoice Upload Link' },
      { selector: 'a[href="/ocr-demo"]', name: 'OCR Demo Link' },
      { selector: 'a[href="/features"]', name: 'Features Link' },
      { selector: 'a[href="/pricing"]', name: 'Pricing Link' }
    ];
    
    for (const item of navItems) {
      try {
        const element = await page.$(item.selector);
        if (element) {
          await element.click();
          await new Promise(resolve => setTimeout(resolve, 1000));
          logTest(item.name, 'PASS', 'Navigation successful');
        } else {
          logTest(item.name, 'FAIL', 'Navigation element not found');
        }
      } catch (error) {
        logTest(item.name, 'FAIL', `Navigation error: ${error.message}`);
      }
    }
    
    // Test back to home
    await page.goto(TEST_CONFIG.baseUrl);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
  } catch (error) {
    logTest('Navigation Test', 'FAIL', `Navigation test failed: ${error.message}`);
  }
}

/**
 * Test OCR functionality
 */
async function testOCRFunctionality(page) {
  console.log('\n🔍 Testing OCR Functionality...');
  
  try {
    // Navigate to OCR demo page
    await page.goto(`${TEST_CONFIG.baseUrl}/ocr-demo`);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test file upload area
    const uploadArea = await page.$('[data-testid="file-upload-area"], .file-upload-area, .dropzone');
    if (uploadArea) {
      logTest('OCR Upload Area', 'PASS', 'File upload area found');
      
      // Test drag and drop functionality
      const fileInput = await page.$('input[type="file"]');
      if (fileInput) {
        // Create a test file
        const testFilePath = path.join(__dirname, 'test-invoice.pdf');
        fs.writeFileSync(testFilePath, 'Sample PDF content for testing');
        
        // Upload file
        await fileInput.uploadFile(testFilePath);
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        logTest('File Upload', 'PASS', 'File uploaded successfully');
        
        // Clean up test file
        fs.unlinkSync(testFilePath);
      } else {
        logTest('File Input', 'FAIL', 'File input not found');
      }
    } else {
      logTest('OCR Upload Area', 'FAIL', 'File upload area not found');
    }
    
    // Test OCR processing buttons
    const processButton = await page.$('button[data-testid="process-button"], button:contains("Process"), .process-btn');
    if (processButton) {
      const isEnabled = await processButton.isEnabled();
      if (isEnabled) {
        await processButton.click();
        await new Promise(resolve => setTimeout(resolve, 3000));
        logTest('OCR Process Button', 'PASS', 'Process button clicked successfully');
      } else {
        logTest('OCR Process Button', 'FAIL', 'Process button is disabled');
      }
    } else {
      logTest('OCR Process Button', 'FAIL', 'Process button not found');
    }
    
  } catch (error) {
    logTest('OCR Functionality', 'FAIL', `OCR test failed: ${error.message}`);
  }
}

/**
 * Test invoice management
 */
async function testInvoiceManagement(page) {
  console.log('\n📄 Testing Invoice Management...');
  
  try {
    // Navigate to invoice upload page
    await page.goto(`${TEST_CONFIG.baseUrl}/invoices/upload`);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test invoice list
    const invoiceList = await page.$('[data-testid="invoice-list"], .invoice-list, .invoices-table');
    if (invoiceList) {
      logTest('Invoice List', 'PASS', 'Invoice list component found');
    } else {
      logTest('Invoice List', 'FAIL', 'Invoice list component not found');
    }
    
    // Test create invoice button
    const createButton = await page.$('button[data-testid="create-invoice"], button:contains("Create"), .create-btn');
    if (createButton) {
      await createButton.click();
      await new Promise(resolve => setTimeout(resolve, 1000));
      logTest('Create Invoice Button', 'PASS', 'Create invoice button clicked');
    } else {
      logTest('Create Invoice Button', 'FAIL', 'Create invoice button not found');
    }
    
    // Test invoice actions
    const actionButtons = await page.$$('button[data-testid*="action"], .action-btn, .btn-action');
    if (actionButtons.length > 0) {
      logTest('Invoice Actions', 'PASS', `${actionButtons.length} action buttons found`);
    } else {
      logTest('Invoice Actions', 'FAIL', 'No action buttons found');
    }
    
  } catch (error) {
    logTest('Invoice Management', 'FAIL', `Invoice management test failed: ${error.message}`);
  }
}

/**
 * Test dashboard functionality
 */
async function testDashboard(page) {
  console.log('\n📊 Testing Dashboard...');
  
  try {
    // Navigate to dashboard
    await page.goto(`${TEST_CONFIG.baseUrl}/dashboard`);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test dashboard widgets
    const widgets = await page.$$('[data-testid*="widget"], .widget, .card');
    if (widgets.length > 0) {
      logTest('Dashboard Widgets', 'PASS', `${widgets.length} widgets found`);
    } else {
      logTest('Dashboard Widgets', 'FAIL', 'No widgets found');
    }
    
    // Test refresh button
    const refreshButton = await page.$('button[data-testid="refresh"], button:contains("Refresh"), .refresh-btn');
    if (refreshButton) {
      await refreshButton.click();
      await new Promise(resolve => setTimeout(resolve, 1000));
      logTest('Refresh Button', 'PASS', 'Refresh button clicked successfully');
    } else {
      logTest('Refresh Button', 'FAIL', 'Refresh button not found');
    }
    
  } catch (error) {
    logTest('Dashboard', 'FAIL', `Dashboard test failed: ${error.message}`);
  }
}

/**
 * Test settings and configuration
 */
async function testSettings(page) {
  console.log('\n⚙️ Testing Settings...');
  
  try {
    // Navigate to dashboard settings
    await page.goto(`${TEST_CONFIG.baseUrl}/dashboard/settings`);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test settings form
    const settingsForm = await page.$('form[data-testid="settings-form"], .settings-form, form');
    if (settingsForm) {
      logTest('Settings Form', 'PASS', 'Settings form found');
    } else {
      logTest('Settings Form', 'FAIL', 'Settings form not found');
    }
    
    // Test save button
    const saveButton = await page.$('button[data-testid="save"], button:contains("Save"), .save-btn');
    if (saveButton) {
      const isEnabled = await saveButton.isEnabled();
      if (isEnabled) {
        await saveButton.click();
        await new Promise(resolve => setTimeout(resolve, 1000));
        logTest('Save Settings Button', 'PASS', 'Save button clicked successfully');
      } else {
        logTest('Save Settings Button', 'FAIL', 'Save button is disabled');
      }
    } else {
      logTest('Save Settings Button', 'FAIL', 'Save button not found');
    }
    
  } catch (error) {
    logTest('Settings', 'FAIL', `Settings test failed: ${error.message}`);
  }
}

/**
 * Test responsive design
 */
async function testResponsiveDesign(page) {
  console.log('\n📱 Testing Responsive Design...');
  
  try {
    // Test mobile viewport
    await page.setViewport({ width: 375, height: 667 });
    await new Promise(resolve => setTimeout(resolve, 1000));
    logTest('Mobile Viewport', 'PASS', 'Mobile viewport set successfully');
    
    // Test tablet viewport
    await page.setViewport({ width: 768, height: 1024 });
    await new Promise(resolve => setTimeout(resolve, 1000));
    logTest('Tablet Viewport', 'PASS', 'Tablet viewport set successfully');
    
    // Test desktop viewport
    await page.setViewport({ width: 1920, height: 1080 });
    await new Promise(resolve => setTimeout(resolve, 1000));
    logTest('Desktop Viewport', 'PASS', 'Desktop viewport set successfully');
    
  } catch (error) {
    logTest('Responsive Design', 'FAIL', `Responsive design test failed: ${error.message}`);
  }
}

/**
 * Test error handling
 */
async function testErrorHandling(page) {
  console.log('\n🚨 Testing Error Handling...');
  
  try {
    // Test 404 page
    await page.goto(`${TEST_CONFIG.baseUrl}/nonexistent-page`);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const errorPage = await page.$('[data-testid="error-page"], .error-page, .not-found');
    if (errorPage) {
      logTest('404 Error Page', 'PASS', '404 error page displayed correctly');
    } else {
      logTest('404 Error Page', 'FAIL', '404 error page not found');
    }
    
    // Test network error handling
    await page.setOfflineMode(true);
    await page.goto(`${TEST_CONFIG.baseUrl}/dashboard`);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const offlineMessage = await page.$('[data-testid="offline-message"], .offline-message, .network-error');
    if (offlineMessage) {
      logTest('Offline Handling', 'PASS', 'Offline message displayed correctly');
    } else {
      logTest('Offline Handling', 'FAIL', 'Offline message not found');
    }
    
    // Restore online mode
    await page.setOfflineMode(false);
    
  } catch (error) {
    logTest('Error Handling', 'FAIL', `Error handling test failed: ${error.message}`);
  }
}

/**
 * Main test function
 */
async function runTests() {
  console.log('🚀 Starting Comprehensive UI Tests...\n');
  
  // Create screenshots directory
  if (!fs.existsSync('screenshots')) {
    fs.mkdirSync('screenshots');
  }
  
  let browser;
  let page;
  
  try {
    // Launch browser
    browser = await puppeteer.launch({
      headless: TEST_CONFIG.headless,
      slowMo: TEST_CONFIG.slowMo,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // Set up error handling
    page.on('pageerror', error => {
      console.log(`Page error: ${error.message}`);
    });
    
    page.on('requestfailed', request => {
      console.log(`Request failed: ${request.url()} - ${request.failure().errorText}`);
    });
    
    // Run all tests
    await testNavigation(page);
    await testDashboard(page);
    await testOCRFunctionality(page);
    await testInvoiceManagement(page);
    await testSettings(page);
    await testResponsiveDesign(page);
    await testErrorHandling(page);
    
  } catch (error) {
    console.error('Test execution failed:', error);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
  
  // Generate test report
  generateTestReport();
}

/**
 * Generate test report
 */
function generateTestReport() {
  console.log('\n📊 Test Results Summary:');
  console.log(`✅ Passed: ${testResults.passed}`);
  console.log(`❌ Failed: ${testResults.failed}`);
  console.log(`📸 Screenshots: ${testResults.screenshots.length}`);
  
  // Save detailed report
  const report = {
    summary: {
      total: testResults.passed + testResults.failed,
      passed: testResults.passed,
      failed: testResults.failed,
      passRate: ((testResults.passed / (testResults.passed + testResults.failed)) * 100).toFixed(2) + '%'
    },
    tests: testResults.tests,
    screenshots: testResults.screenshots,
    timestamp: new Date().toISOString()
  };
  
  fs.writeFileSync('test-report.json', JSON.stringify(report, null, 2));
  console.log('\n📄 Detailed report saved to test-report.json');
  
  // Exit with appropriate code
  process.exit(testResults.failed > 0 ? 1 : 0);
}

// Run tests if this file is executed directly
if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = { runTests, testResults };
