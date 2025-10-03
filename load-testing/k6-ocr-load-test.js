/**
 * K6 Load Test for OCR Processing
 * Tests concurrent invoice uploads and OCR processing
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const ocrSuccessRate = new Rate('ocr_success_rate');
const ocrProcessingTime = new Trend('ocr_processing_time');
const ocrErrorCount = new Counter('ocr_error_count');
const invoiceUploadTime = new Trend('invoice_upload_time');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up to 10 users
    { duration: '5m', target: 50 },   // Ramp up to 50 users
    { duration: '10m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
    ocr_success_rate: ['rate>0.9'],    // OCR success rate must be above 90%
    ocr_processing_time: ['p(95)<5000'], // 95% of OCR processing must complete below 5s
  },
};

// Test data
const testInvoices = [
  {
    filename: 'invoice-1.pdf',
    content: 'base64-encoded-pdf-content-1',
    supplier: 'Acme Corp',
    amount: 1000.00
  },
  {
    filename: 'invoice-2.pdf', 
    content: 'base64-encoded-pdf-content-2',
    supplier: 'Tech Solutions Inc',
    amount: 2500.00
  },
  {
    filename: 'invoice-3.pdf',
    content: 'base64-encoded-pdf-content-3', 
    supplier: 'Global Services Ltd',
    amount: 500.00
  }
];

// Authentication token (would be obtained from login)
let authToken = '';

export function setup() {
  // Login and get authentication token
  const loginResponse = http.post('http://localhost:8000/api/v1/auth/login', {
    email: 'test@example.com',
    password: 'testpassword123'
  });
  
  if (loginResponse.status === 200) {
    const loginData = JSON.parse(loginResponse.body);
    return { token: loginData.access_token };
  }
  
  throw new Error('Failed to authenticate');
}

export default function(data) {
  const token = data.token;
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
  
  // Select random test invoice
  const invoice = testInvoices[Math.floor(Math.random() * testInvoices.length)];
  
  // Test 1: Upload invoice for OCR processing
  const uploadStart = Date.now();
  const uploadResponse = http.post('http://localhost:8000/api/v1/ocr/process', {
    filename: invoice.filename,
    content: invoice.content,
    supplier_name: invoice.supplier,
    expected_amount: invoice.amount
  }, { headers });
  
  const uploadTime = Date.now() - uploadStart;
  invoiceUploadTime.add(uploadTime);
  
  const uploadSuccess = check(uploadResponse, {
    'invoice upload successful': (r) => r.status === 200,
    'upload response time < 2s': (r) => r.timings.duration < 2000,
  });
  
  if (!uploadSuccess) {
    ocrErrorCount.add(1);
    return;
  }
  
  const uploadData = JSON.parse(uploadResponse.body);
  const processingId = uploadData.processing_id;
  
  // Test 2: Poll for OCR completion
  let attempts = 0;
  const maxAttempts = 30; // 5 minutes max
  let ocrComplete = false;
  let ocrResult = null;
  
  const ocrStart = Date.now();
  
  while (attempts < maxAttempts && !ocrComplete) {
    sleep(10); // Wait 10 seconds between polls
    attempts++;
    
    const statusResponse = http.get(
      `http://localhost:8000/api/v1/ocr/status/${processingId}`,
      { headers }
    );
    
    const statusSuccess = check(statusResponse, {
      'OCR status check successful': (r) => r.status === 200,
    });
    
    if (!statusSuccess) {
      ocrErrorCount.add(1);
      return;
    }
    
    const statusData = JSON.parse(statusResponse.body);
    
    if (statusData.status === 'completed') {
      ocrComplete = true;
      ocrResult = statusData;
    } else if (statusData.status === 'failed') {
      ocrErrorCount.add(1);
      return;
    }
  }
  
  const ocrTime = Date.now() - ocrStart;
  ocrProcessingTime.add(ocrTime);
  
  // Test 3: Verify OCR results
  if (ocrComplete && ocrResult) {
    const ocrSuccess = check(ocrResult, {
      'OCR extraction successful': (r) => r.extracted_data !== null,
      'supplier name extracted': (r) => r.extracted_data.supplier_name === invoice.supplier,
      'amount extracted correctly': (r) => Math.abs(r.extracted_data.total_amount - invoice.amount) < 0.01,
      'confidence score acceptable': (r) => r.confidence_score > 0.8,
    });
    
    ocrSuccessRate.add(ocrSuccess);
  } else {
    ocrErrorCount.add(1);
  }
  
  // Test 4: Create invoice from OCR result
  if (ocrComplete && ocrResult && ocrResult.extracted_data) {
    const createResponse = http.post('http://localhost:8000/api/v1/invoices', {
      invoice_number: ocrResult.extracted_data.invoice_number,
      supplier_name: ocrResult.extracted_data.supplier_name,
      supplier_email: ocrResult.extracted_data.supplier_email,
      total_amount: ocrResult.extracted_data.total_amount,
      currency: ocrResult.extracted_data.currency,
      invoice_date: ocrResult.extracted_data.invoice_date,
      ocr_data: ocrResult.extracted_data,
      ocr_confidence: ocrResult.confidence_score
    }, { headers });
    
    check(createResponse, {
      'invoice creation successful': (r) => r.status === 201,
      'invoice creation time < 1s': (r) => r.timings.duration < 1000,
    });
  }
  
  // Random sleep between 1-3 seconds
  sleep(Math.random() * 2 + 1);
}

export function teardown(data) {
  console.log('OCR Load Test completed');
}
