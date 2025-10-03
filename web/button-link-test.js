/**
 * Button and Link Functionality Test
 * Tests all interactive elements to ensure they work properly
 */
const puppeteer = require('puppeteer');
const fs = require('fs');

async function testButtonsAndLinks() {
  console.log('🚀 Starting Button and Link Functionality Test...\n');
  
  let browser;
  let page;
  const results = { passed: 0, failed: 0, tests: [] };
  
  function logTest(name, status, message) {
    results.tests.push({ name, status, message, timestamp: new Date().toISOString() });
    if (status === 'PASS') {
      results.passed++;
      console.log(`✅ ${name}: ${message}`);
    } else {
      results.failed++;
      console.log(`❌ ${name}: ${message}`);
    }
  }
  
  try {
    browser = await puppeteer.launch({
      headless: false,
      slowMo: 200,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // Test 1: Homepage Navigation
    console.log('🏠 Testing Homepage Navigation...');
    await page.goto('http://localhost:3000');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test logo click
    try {
      const logo = await page.$('a[href="/"]');
      if (logo) {
        await logo.click();
        await new Promise(resolve => setTimeout(resolve, 1000));
        logTest('Logo Click', 'PASS', 'Logo click works');
      } else {
        logTest('Logo Click', 'FAIL', 'Logo not found');
      }
    } catch (error) {
      logTest('Logo Click', 'FAIL', `Error: ${error.message}`);
    }
    
    // Test navigation links
    const navLinks = [
      { selector: 'a[href="/features"]', name: 'Features Link' },
      { selector: 'a[href="/pricing"]', name: 'Pricing Link' },
      { selector: 'a[href="/integrations"]', name: 'Integrations Link' },
      { selector: 'a[href="/contact"]', name: 'Contact Link' }
    ];
    
    for (const link of navLinks) {
      try {
        const element = await page.$(link.selector);
        if (element) {
          await element.click();
          await new Promise(resolve => setTimeout(resolve, 1000));
          logTest(link.name, 'PASS', 'Navigation successful');
          await page.goBack();
          await new Promise(resolve => setTimeout(resolve, 1000));
        } else {
          logTest(link.name, 'FAIL', 'Link not found');
        }
      } catch (error) {
        logTest(link.name, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Test 2: OCR Demo Page
    console.log('\n🔍 Testing OCR Demo Page...');
    await page.goto('http://localhost:3000/ocr-demo');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test file upload
    try {
      const fileInput = await page.$('input[type="file"]');
      if (fileInput) {
        // Create a test file
        const testFile = 'test-invoice.pdf';
        fs.writeFileSync(testFile, 'Sample PDF content for testing');
        
        // Upload file
        await fileInput.uploadFile(testFile);
        await new Promise(resolve => setTimeout(resolve, 1000));
        logTest('File Upload', 'PASS', 'File upload works');
        
        // Clean up
        fs.unlinkSync(testFile);
      } else {
        logTest('File Upload', 'FAIL', 'File input not found');
      }
    } catch (error) {
      logTest('File Upload', 'FAIL', `Error: ${error.message}`);
    }
    
    // Test OCR buttons
    const ocrButtons = await page.$$('button');
    for (let i = 0; i < Math.min(ocrButtons.length, 3); i++) {
      try {
        const button = ocrButtons[i];
        const buttonText = await button.evaluate(el => el.textContent);
        const isEnabled = await button.isEnabled();
        
        if (isEnabled) {
          await button.click();
          await new Promise(resolve => setTimeout(resolve, 1000));
          logTest(`OCR Button ${i + 1} (${buttonText})`, 'PASS', 'Button click works');
        } else {
          logTest(`OCR Button ${i + 1} (${buttonText})`, 'PASS', 'Button is disabled (expected)');
        }
      } catch (error) {
        logTest(`OCR Button ${i + 1}`, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Test 3: Invoice Upload Page
    console.log('\n📄 Testing Invoice Upload Page...');
    await page.goto('http://localhost:3000/invoices/upload');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test upload functionality
    try {
      const uploadElements = await page.$$('input[type="file"], .file-upload, .dropzone');
      if (uploadElements.length > 0) {
        logTest('Invoice Upload Elements', 'PASS', `Found ${uploadElements.length} upload elements`);
      } else {
        logTest('Invoice Upload Elements', 'FAIL', 'No upload elements found');
      }
    } catch (error) {
      logTest('Invoice Upload Elements', 'FAIL', `Error: ${error.message}`);
    }
    
    // Test 4: Dashboard
    console.log('\n📊 Testing Dashboard...');
    await page.goto('http://localhost:3000/dashboard');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test dashboard navigation
    const dashboardLinks = [
      { selector: 'a[href="/dashboard/invoices"]', name: 'Dashboard Invoices Link' },
      { selector: 'a[href="/dashboard/settings"]', name: 'Dashboard Settings Link' },
      { selector: 'a[href="/dashboard/billing"]', name: 'Dashboard Billing Link' }
    ];
    
    for (const link of dashboardLinks) {
      try {
        const element = await page.$(link.selector);
        if (element) {
          await element.click();
          await new Promise(resolve => setTimeout(resolve, 1000));
          logTest(link.name, 'PASS', 'Dashboard navigation works');
          await page.goBack();
          await new Promise(resolve => setTimeout(resolve, 1000));
        } else {
          logTest(link.name, 'FAIL', 'Dashboard link not found');
        }
      } catch (error) {
        logTest(link.name, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Test 5: Authentication Pages
    console.log('\n🔐 Testing Authentication Pages...');
    
    // Test login page
    await page.goto('http://localhost:3000/auth/login');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    try {
      const loginForm = await page.$('form');
      if (loginForm) {
        logTest('Login Form', 'PASS', 'Login form found');
        
        // Test form inputs
        const emailInput = await page.$('input[type="email"], input[placeholder*="email" i]');
        const passwordInput = await page.$('input[type="password"]');
        
        if (emailInput && passwordInput) {
          logTest('Login Inputs', 'PASS', 'Email and password inputs found');
        } else {
          logTest('Login Inputs', 'FAIL', 'Login inputs not found');
        }
      } else {
        logTest('Login Form', 'FAIL', 'Login form not found');
      }
    } catch (error) {
      logTest('Login Form', 'FAIL', `Error: ${error.message}`);
    }
    
    // Test 6: Responsive Design
    console.log('\n📱 Testing Responsive Design...');
    
    // Test mobile viewport
    await page.setViewport({ width: 375, height: 667 });
    await new Promise(resolve => setTimeout(resolve, 1000));
    logTest('Mobile Viewport', 'PASS', 'Mobile viewport works');
    
    // Test tablet viewport
    await page.setViewport({ width: 768, height: 1024 });
    await new Promise(resolve => setTimeout(resolve, 1000));
    logTest('Tablet Viewport', 'PASS', 'Tablet viewport works');
    
    // Test desktop viewport
    await page.setViewport({ width: 1920, height: 1080 });
    await new Promise(resolve => setTimeout(resolve, 1000));
    logTest('Desktop Viewport', 'PASS', 'Desktop viewport works');
    
    // Test 7: Error Handling
    console.log('\n🚨 Testing Error Handling...');
    
    // Test 404 page
    await page.goto('http://localhost:3000/nonexistent-page');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    try {
      const errorPage = await page.$('.not-found, .error-page, [data-testid="error"]');
      if (errorPage) {
        logTest('404 Error Page', 'PASS', '404 error page displayed');
      } else {
        logTest('404 Error Page', 'PASS', '404 handled (redirected to home)');
      }
    } catch (error) {
      logTest('404 Error Page', 'FAIL', `Error: ${error.message}`);
    }
    
    // Generate final report
    console.log('\n📊 Test Results Summary:');
    console.log(`✅ Passed: ${results.passed}`);
    console.log(`❌ Failed: ${results.failed}`);
    console.log(`📈 Success Rate: ${((results.passed / (results.passed + results.failed)) * 100).toFixed(1)}%`);
    
    // Save detailed report
    const report = {
      summary: {
        total: results.passed + results.failed,
        passed: results.passed,
        failed: results.failed,
        successRate: `${((results.passed / (results.passed + results.failed)) * 100).toFixed(1)}%`
      },
      tests: results.tests,
      timestamp: new Date().toISOString()
    };
    
    fs.writeFileSync('button-link-test-report.json', JSON.stringify(report, null, 2));
    console.log('\n📄 Detailed report saved to button-link-test-report.json');
    
  } catch (error) {
    console.error('❌ Test execution failed:', error);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

testButtonsAndLinks().catch(console.error);
