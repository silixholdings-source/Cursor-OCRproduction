/**
 * Simple UI Test - Check basic functionality
 */
const puppeteer = require('puppeteer');

async function runSimpleTest() {
  console.log('🚀 Starting Simple UI Test...\n');
  
  let browser;
  let page;
  
  try {
    // Launch browser
    browser = await puppeteer.launch({
      headless: false,
      slowMo: 100,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // Test homepage
    console.log('📄 Testing Homepage...');
    await page.goto('http://localhost:3000');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check if page loaded
    const title = await page.title();
    console.log(`✅ Page title: ${title}`);
    
    // Check for main elements
    const logo = await page.$('a[href="/"]');
    if (logo) {
      console.log('✅ Logo found');
    } else {
      console.log('❌ Logo not found');
    }
    
    // Check for navigation links
    const navLinks = await page.$$('a[href]');
    console.log(`✅ Found ${navLinks.length} navigation links`);
    
    // Test OCR demo page
    console.log('\n🔍 Testing OCR Demo Page...');
    await page.goto('http://localhost:3000/ocr-demo');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const ocrTitle = await page.title();
    console.log(`✅ OCR Demo page title: ${ocrTitle}`);
    
    // Check for file upload elements
    const fileInputs = await page.$$('input[type="file"]');
    console.log(`✅ Found ${fileInputs.length} file input elements`);
    
    // Check for buttons
    const buttons = await page.$$('button');
    console.log(`✅ Found ${buttons.length} buttons`);
    
    // Test invoice upload page
    console.log('\n📄 Testing Invoice Upload Page...');
    await page.goto('http://localhost:3000/invoices/upload');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const invoiceTitle = await page.title();
    console.log(`✅ Invoice Upload page title: ${invoiceTitle}`);
    
    // Test dashboard
    console.log('\n📊 Testing Dashboard...');
    await page.goto('http://localhost:3000/dashboard');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const dashboardTitle = await page.title();
    console.log(`✅ Dashboard page title: ${dashboardTitle}`);
    
    console.log('\n✅ Simple test completed successfully!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

runSimpleTest().catch(console.error);
