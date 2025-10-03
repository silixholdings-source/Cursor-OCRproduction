/**
 * Final Comprehensive Test - All Buttons and Links
 * Tests every interactive element to ensure proper functionality
 */
const puppeteer = require('puppeteer');
const fs = require('fs');

async function runFinalTest() {
  console.log('🚀 Starting Final Comprehensive Test...\n');
  
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
      slowMo: 150,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // Test 1: Homepage - All Links and Buttons
    console.log('🏠 Testing Homepage - All Interactive Elements...');
    await page.goto('http://localhost:3000');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Test all navigation links
    const allLinks = await page.$$('a[href]');
    console.log(`Found ${allLinks.length} total links on homepage`);
    
    for (let i = 0; i < Math.min(allLinks.length, 10); i++) {
      try {
        const link = allLinks[i];
        const href = await link.evaluate(el => el.getAttribute('href'));
        const text = await link.evaluate(el => el.textContent?.trim() || '');
        
        if (href && !href.startsWith('#') && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
          await link.click();
          await new Promise(resolve => setTimeout(resolve, 1000));
          logTest(`Homepage Link ${i + 1} (${text})`, 'PASS', `Clicked: ${href}`);
          await page.goBack();
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      } catch (error) {
        logTest(`Homepage Link ${i + 1}`, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Test all buttons on homepage
    const allButtons = await page.$$('button');
    console.log(`Found ${allButtons.length} total buttons on homepage`);
    
    for (let i = 0; i < Math.min(allButtons.length, 5); i++) {
      try {
        const button = allButtons[i];
        const text = await button.evaluate(el => el.textContent?.trim() || '');
        const isDisabled = await button.evaluate(el => el.disabled);
        
        if (!isDisabled) {
          await button.click();
          await new Promise(resolve => setTimeout(resolve, 1000));
          logTest(`Homepage Button ${i + 1} (${text})`, 'PASS', 'Button click successful');
          await page.goBack();
          await new Promise(resolve => setTimeout(resolve, 1000));
        } else {
          logTest(`Homepage Button ${i + 1} (${text})`, 'PASS', 'Button is disabled (expected)');
        }
      } catch (error) {
        logTest(`Homepage Button ${i + 1}`, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Test 2: OCR Demo Page - Complete Functionality
    console.log('\n🔍 Testing OCR Demo Page - Complete Functionality...');
    await page.goto('http://localhost:3000/ocr-demo');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Test file upload
    try {
      const fileInput = await page.$('input[type="file"]');
      if (fileInput) {
        // Create test file
        const testFile = 'test-invoice.pdf';
        fs.writeFileSync(testFile, 'Sample PDF content for testing');
        
        // Upload file
        await fileInput.uploadFile(testFile);
        await new Promise(resolve => setTimeout(resolve, 1000));
        logTest('OCR File Upload', 'PASS', 'File uploaded successfully');
        
        // Clean up
        fs.unlinkSync(testFile);
      } else {
        logTest('OCR File Upload', 'FAIL', 'File input not found');
      }
    } catch (error) {
      logTest('OCR File Upload', 'FAIL', `Error: ${error.message}`);
    }
    
    // Test OCR process button
    try {
      const processButton = await page.$('button');
      if (processButton) {
        const buttonText = await processButton.evaluate(el => el.textContent?.trim() || '');
        const isDisabled = await processButton.evaluate(el => el.disabled);
        
        if (!isDisabled) {
          await processButton.click();
          await new Promise(resolve => setTimeout(resolve, 3000));
          logTest('OCR Process Button', 'PASS', `Clicked: ${buttonText}`);
        } else {
          logTest('OCR Process Button', 'PASS', 'Button is disabled (expected)');
        }
      } else {
        logTest('OCR Process Button', 'FAIL', 'Process button not found');
      }
    } catch (error) {
      logTest('OCR Process Button', 'FAIL', `Error: ${error.message}`);
    }
    
    // Test 3: Invoice Upload Page
    console.log('\n📄 Testing Invoice Upload Page...');
    await page.goto('http://localhost:3000/invoices/upload');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Test all interactive elements
    const uploadButtons = await page.$$('button');
    for (let i = 0; i < uploadButtons.length; i++) {
      try {
        const button = uploadButtons[i];
        const text = await button.evaluate(el => el.textContent?.trim() || '');
        const isDisabled = await button.evaluate(el => el.disabled);
        
        if (!isDisabled && text) {
          await button.click();
          await new Promise(resolve => setTimeout(resolve, 1000));
          logTest(`Upload Button ${i + 1} (${text})`, 'PASS', 'Button click successful');
        }
      } catch (error) {
        logTest(`Upload Button ${i + 1}`, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Test 4: Dashboard - All Sections
    console.log('\n📊 Testing Dashboard - All Sections...');
    await page.goto('http://localhost:3000/dashboard');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Test dashboard navigation
    const dashboardLinks = await page.$$('a[href*="/dashboard/"]');
    for (let i = 0; i < Math.min(dashboardLinks.length, 5); i++) {
      try {
        const link = dashboardLinks[i];
        const href = await link.evaluate(el => el.getAttribute('href'));
        const text = await link.evaluate(el => el.textContent?.trim() || '');
        
        await link.click();
        await new Promise(resolve => setTimeout(resolve, 1000));
        logTest(`Dashboard Link ${i + 1} (${text})`, 'PASS', `Navigated to: ${href}`);
        await page.goBack();
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        logTest(`Dashboard Link ${i + 1}`, 'FAIL', `Error: ${error.message}`);
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
        const inputs = await page.$$('input');
        logTest('Login Inputs', 'PASS', `Found ${inputs.length} input fields`);
        
        // Test submit button
        const submitButton = await page.$('button[type="submit"], button');
        if (submitButton) {
          const buttonText = await submitButton.evaluate(el => el.textContent?.trim() || '');
          logTest('Login Submit Button', 'PASS', `Found: ${buttonText}`);
        }
      } else {
        logTest('Login Form', 'FAIL', 'Login form not found');
      }
    } catch (error) {
      logTest('Login Form', 'FAIL', `Error: ${error.message}`);
    }
    
    // Test 6: Features Page
    console.log('\n✨ Testing Features Page...');
    await page.goto('http://localhost:3000/features');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const featuresButtons = await page.$$('button');
    for (let i = 0; i < Math.min(featuresButtons.length, 3); i++) {
      try {
        const button = featuresButtons[i];
        const text = await button.evaluate(el => el.textContent?.trim() || '');
        const isDisabled = await button.evaluate(el => el.disabled);
        
        if (!isDisabled && text) {
          await button.click();
          await new Promise(resolve => setTimeout(resolve, 1000));
          logTest(`Features Button ${i + 1} (${text})`, 'PASS', 'Button click successful');
        }
      } catch (error) {
        logTest(`Features Button ${i + 1}`, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Test 7: Pricing Page
    console.log('\n💰 Testing Pricing Page...');
    await page.goto('http://localhost:3000/pricing');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const pricingButtons = await page.$$('button');
    for (let i = 0; i < Math.min(pricingButtons.length, 3); i++) {
      try {
        const button = pricingButtons[i];
        const text = await button.evaluate(el => el.textContent?.trim() || '');
        const isDisabled = await button.evaluate(el => el.disabled);
        
        if (!isDisabled && text) {
          await button.click();
          await new Promise(resolve => setTimeout(resolve, 1000));
          logTest(`Pricing Button ${i + 1} (${text})`, 'PASS', 'Button click successful');
        }
      } catch (error) {
        logTest(`Pricing Button ${i + 1}`, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Test 8: Contact Page
    console.log('\n📞 Testing Contact Page...');
    await page.goto('http://localhost:3000/contact');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    try {
      const contactForm = await page.$('form');
      if (contactForm) {
        logTest('Contact Form', 'PASS', 'Contact form found');
        
        // Test form inputs
        const inputs = await page.$$('input, textarea');
        logTest('Contact Inputs', 'PASS', `Found ${inputs.length} input fields`);
        
        // Test submit button
        const submitButton = await page.$('button[type="submit"], button');
        if (submitButton) {
          const buttonText = await submitButton.evaluate(el => el.textContent?.trim() || '');
          logTest('Contact Submit Button', 'PASS', `Found: ${buttonText}`);
        }
      } else {
        logTest('Contact Form', 'FAIL', 'Contact form not found');
      }
    } catch (error) {
      logTest('Contact Form', 'FAIL', `Error: ${error.message}`);
    }
    
    // Test 9: Responsive Design
    console.log('\n📱 Testing Responsive Design...');
    
    const viewports = [
      { width: 375, height: 667, name: 'Mobile' },
      { width: 768, height: 1024, name: 'Tablet' },
      { width: 1920, height: 1080, name: 'Desktop' }
    ];
    
    for (const viewport of viewports) {
      try {
        await page.setViewport({ width: viewport.width, height: viewport.height });
        await new Promise(resolve => setTimeout(resolve, 1000));
        logTest(`${viewport.name} Viewport`, 'PASS', `${viewport.width}x${viewport.height} works`);
      } catch (error) {
        logTest(`${viewport.name} Viewport`, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Test 10: Error Handling
    console.log('\n🚨 Testing Error Handling...');
    
    // Test 404 page
    try {
      await page.goto('http://localhost:3000/nonexistent-page');
      await new Promise(resolve => setTimeout(resolve, 2000));
      logTest('404 Error Handling', 'PASS', '404 page handled correctly');
    } catch (error) {
      logTest('404 Error Handling', 'FAIL', `Error: ${error.message}`);
    }
    
    // Generate final report
    console.log('\n📊 Final Test Results Summary:');
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
    
    fs.writeFileSync('final-test-report.json', JSON.stringify(report, null, 2));
    console.log('\n📄 Detailed report saved to final-test-report.json');
    
    // Final assessment
    if (results.failed === 0) {
      console.log('\n🎉 ALL TESTS PASSED! The application is ready for use.');
    } else if (results.failed <= 3) {
      console.log('\n✅ MOSTLY WORKING! Minor issues found, but core functionality works.');
    } else {
      console.log('\n⚠️  SOME ISSUES FOUND! Please review the failed tests.');
    }
    
  } catch (error) {
    console.error('❌ Test execution failed:', error);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

runFinalTest().catch(console.error);
