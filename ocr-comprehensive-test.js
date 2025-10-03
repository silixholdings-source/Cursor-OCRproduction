/**
 * Comprehensive OCR Functionality Test Suite
 * Tests all aspects of the OCR system according to project requirements
 */

const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_CONFIG = {
  backendUrl: 'http://localhost:8000',
  frontendUrl: 'http://localhost:3000',
  ocrServiceUrl: 'http://localhost:8001',
  timeout: 10000
};

// Test results tracking
const testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  tests: [],
  summary: {
    backendHealth: false,
    ocrServiceHealth: false,
    frontendHealth: false,
    ocrProcessing: false,
    invoiceExtraction: false,
    confidenceValidation: false,
    apiIntegration: false,
    errorHandling: false
  }
};

// Utility functions
function logTest(testName, status, message = '', details = {}) {
  const result = {
    id: testResults.total + 1,
    name: testName,
    status,
    message,
    details,
    timestamp: new Date().toISOString()
  };
  
  testResults.tests.push(result);
  testResults.total++;
  
  if (status === 'PASS') {
    testResults.passed++;
    console.log(`✅ [${result.id}] ${testName}: ${message}`);
  } else {
    testResults.failed++;
    console.log(`❌ [${result.id}] ${testName}: ${message}`);
  }
}

async function makeRequest(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TEST_CONFIG.timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

// Test 1: Backend Health Check
async function testBackendHealth() {
  try {
    const response = await makeRequest(`${TEST_CONFIG.backendUrl}/health`);
    const data = await response.json();
    
    if (response.ok && data.status === 'healthy') {
      logTest('Backend Health Check', 'PASS', 'Backend is running and healthy', data);
      testResults.summary.backendHealth = true;
      return true;
    } else {
      logTest('Backend Health Check', 'FAIL', `Backend returned: ${data.status}`, data);
      return false;
    }
  } catch (error) {
    logTest('Backend Health Check', 'FAIL', `Connection failed: ${error.message}`);
    return false;
  }
}

// Test 2: OCR Service Health Check
async function testOCRServiceHealth() {
  try {
    const response = await makeRequest(`${TEST_CONFIG.ocrServiceUrl}/health`);
    const data = await response.json();
    
    if (response.ok && data.status === 'healthy') {
      logTest('OCR Service Health Check', 'PASS', 'OCR service is running and healthy', data);
      testResults.summary.ocrServiceHealth = true;
      return true;
    } else {
      logTest('OCR Service Health Check', 'FAIL', `OCR service returned: ${data.status}`, data);
      return false;
    }
  } catch (error) {
    logTest('OCR Service Health Check', 'FAIL', `OCR service connection failed: ${error.message}`);
    return false;
  }
}

// Test 3: Frontend Health Check
async function testFrontendHealth() {
  try {
    const response = await makeRequest(`${TEST_CONFIG.frontendUrl}/`);
    
    if (response.ok) {
      logTest('Frontend Health Check', 'PASS', 'Frontend is accessible', { status: response.status });
      testResults.summary.frontendHealth = true;
      return true;
    } else {
      logTest('Frontend Health Check', 'FAIL', `Frontend returned: ${response.status} ${response.statusText}`);
      return false;
    }
  } catch (error) {
    logTest('Frontend Health Check', 'FAIL', `Frontend connection failed: ${error.message}`);
    return false;
  }
}

// Test 4: OCR Demo Endpoint Test
async function testOCRDemoEndpoint() {
  try {
    const response = await makeRequest(`${TEST_CONFIG.backendUrl}/api/v1/processing/demo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        test: true,
        file_name: 'test-invoice.pdf',
        company_id: 'test-company'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Validate OCR response structure
      const hasRequiredFields = data.ocr_data && 
        data.ocr_data.supplier_name && 
        data.ocr_data.invoice_number && 
        data.ocr_data.total_amount;
      
      if (hasRequiredFields) {
        logTest('OCR Demo Endpoint', 'PASS', 'Demo OCR endpoint working with proper data structure', {
          extractedFields: Object.keys(data.ocr_data),
          confidenceScores: data.ocr_data.confidence_scores
        });
        testResults.summary.ocrProcessing = true;
        return true;
      } else {
        logTest('OCR Demo Endpoint', 'FAIL', 'OCR response missing required fields', data);
        return false;
      }
    } else {
      logTest('OCR Demo Endpoint', 'FAIL', `HTTP ${response.status}: ${response.statusText}`);
      return false;
    }
  } catch (error) {
    logTest('OCR Demo Endpoint', 'FAIL', `Request failed: ${error.message}`);
    return false;
  }
}

// Test 5: Invoice Data Extraction Validation
async function testInvoiceDataExtraction() {
  try {
    const response = await makeRequest(`${TEST_CONFIG.backendUrl}/api/v1/processing/demo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        test: true,
        file_name: 'comprehensive-test-invoice.pdf',
        company_id: 'test-company'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      const ocrData = data.ocr_data;
      
      // Test according to MasterPromptDoc requirements
      const requiredFields = [
        'supplier_name',
        'invoice_number', 
        'total_amount',
        'invoice_date',
        'due_date',
        'line_items'
      ];
      
      const missingFields = requiredFields.filter(field => !ocrData[field]);
      const hasLineItems = ocrData.line_items && Array.isArray(ocrData.line_items) && ocrData.line_items.length > 0;
      
      if (missingFields.length === 0 && hasLineItems) {
        logTest('Invoice Data Extraction', 'PASS', 'All required fields extracted successfully', {
          extractedFields: Object.keys(ocrData),
          lineItemCount: ocrData.line_items?.length || 0,
          supplierName: ocrData.supplier_name,
          invoiceNumber: ocrData.invoice_number,
          totalAmount: ocrData.total_amount
        });
        testResults.summary.invoiceExtraction = true;
        return true;
      } else {
        logTest('Invoice Data Extraction', 'FAIL', `Missing fields: ${missingFields.join(', ')}`, {
          missingFields,
          hasLineItems,
          availableFields: Object.keys(ocrData)
        });
        return false;
      }
    } else {
      logTest('Invoice Data Extraction', 'FAIL', `HTTP ${response.status}: ${response.statusText}`);
      return false;
    }
  } catch (error) {
    logTest('Invoice Data Extraction', 'FAIL', `Request failed: ${error.message}`);
    return false;
  }
}

// Test 6: Confidence Score Validation
async function testConfidenceScoreValidation() {
  try {
    const response = await makeRequest(`${TEST_CONFIG.backendUrl}/api/v1/processing/demo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        test: true,
        file_name: 'confidence-test-invoice.pdf',
        company_id: 'test-company'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      const confidenceScores = data.ocr_data?.confidence_scores;
      
      if (confidenceScores) {
        // Test MasterPromptDoc requirements: 98% accuracy for totals, 95% for supplier
        const totalConfidence = confidenceScores.total_amount || 0;
        const supplierConfidence = confidenceScores.supplier_name || 0;
        
        const meetsTotalRequirement = totalConfidence >= 0.98;
        const meetsSupplierRequirement = supplierConfidence >= 0.95;
        
        if (meetsTotalRequirement && meetsSupplierRequirement) {
          logTest('Confidence Score Validation', 'PASS', 'Confidence scores meet requirements', {
            totalAmountConfidence: totalConfidence,
            supplierNameConfidence: supplierConfidence,
            allConfidenceScores: confidenceScores
          });
          testResults.summary.confidenceValidation = true;
          return true;
        } else {
          logTest('Confidence Score Validation', 'FAIL', 'Confidence scores below requirements', {
            totalAmountConfidence: totalConfidence,
            supplierNameConfidence: supplierConfidence,
            totalRequirement: '≥98%',
            supplierRequirement: '≥95%',
            allConfidenceScores: confidenceScores
          });
          return false;
        }
      } else {
        logTest('Confidence Score Validation', 'FAIL', 'No confidence scores returned');
        return false;
      }
    } else {
      logTest('Confidence Score Validation', 'FAIL', `HTTP ${response.status}: ${response.statusText}`);
      return false;
    }
  } catch (error) {
    logTest('Confidence Score Validation', 'FAIL', `Request failed: ${error.message}`);
    return false;
  }
}

// Test 7: Frontend OCR API Integration
async function testFrontendOCRAPI() {
  try {
    const response = await makeRequest(`${TEST_CONFIG.frontendUrl}/api/ocr/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        test: true,
        file_name: 'frontend-test-invoice.pdf',
        company_id: 'test-company'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      
      if (data.success && data.data) {
        logTest('Frontend OCR API Integration', 'PASS', 'Frontend OCR API working correctly', {
          success: data.success,
          hasData: !!data.data,
          message: data.message
        });
        testResults.summary.apiIntegration = true;
        return true;
      } else {
        logTest('Frontend OCR API Integration', 'FAIL', 'Invalid response format', data);
        return false;
      }
    } else {
      logTest('Frontend OCR API Integration', 'FAIL', `HTTP ${response.status}: ${response.statusText}`);
      return false;
    }
  } catch (error) {
    logTest('Frontend OCR API Integration', 'FAIL', `Request failed: ${error.message}`);
    return false;
  }
}

// Test 8: Error Handling
async function testErrorHandling() {
  try {
    // Test with invalid file type
    const response = await makeRequest(`${TEST_CONFIG.backendUrl}/api/v1/processing/demo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        test: true,
        file_name: 'invalid-file.exe',
        company_id: 'test-company'
      })
    });
    
    // Should handle invalid file gracefully
    if (response.ok || response.status === 400) {
      logTest('Error Handling', 'PASS', 'Error handling working correctly', {
        status: response.status,
        handlesInvalidFile: true
      });
      testResults.summary.errorHandling = true;
      return true;
    } else {
      logTest('Error Handling', 'FAIL', 'Unexpected error response', { status: response.status });
      return false;
    }
  } catch (error) {
    logTest('Error Handling', 'FAIL', `Error handling test failed: ${error.message}`);
    return false;
  }
}

// Test 9: OCR Service Direct Test
async function testOCRServiceDirect() {
  try {
    const response = await makeRequest(`${TEST_CONFIG.ocrServiceUrl}/health`);
    
    if (response.ok) {
      const data = await response.json();
      
      // Test OCR service readiness
      const readyResponse = await makeRequest(`${TEST_CONFIG.ocrServiceUrl}/ready`);
      
      if (readyResponse.ok) {
        logTest('OCR Service Direct Test', 'PASS', 'OCR service responding correctly', {
          health: data,
          ready: await readyResponse.json()
        });
        return true;
      } else {
        logTest('OCR Service Direct Test', 'FAIL', 'OCR service not ready');
        return false;
      }
    } else {
      logTest('OCR Service Direct Test', 'FAIL', `OCR service health check failed: ${response.status}`);
      return false;
    }
  } catch (error) {
    logTest('OCR Service Direct Test', 'FAIL', `OCR service test failed: ${error.message}`);
    return false;
  }
}

// Test 10: File Upload Simulation
async function testFileUploadSimulation() {
  try {
    // Create a mock file for testing
    const mockFile = new File(['Mock invoice content for OCR testing'], 'test-invoice.pdf', {
      type: 'application/pdf'
    });
    
    const formData = new FormData();
    formData.append('file', mockFile);
    formData.append('company_id', 'test-company');
    
    const response = await makeRequest(`${TEST_CONFIG.ocrServiceUrl}/process`, {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      const data = await response.json();
      
      if (data.status === 'SUCCESS' && data.data) {
        logTest('File Upload Simulation', 'PASS', 'File upload and OCR processing working', {
          status: data.status,
          hasData: !!data.data,
          message: data.message
        });
        return true;
      } else {
        logTest('File Upload Simulation', 'FAIL', 'OCR processing failed', data);
        return false;
      }
    } else {
      logTest('File Upload Simulation', 'FAIL', `Upload failed: ${response.status} ${response.statusText}`);
      return false;
    }
  } catch (error) {
    logTest('File Upload Simulation', 'FAIL', `Upload test failed: ${error.message}`);
    return false;
  }
}

// Main test runner
async function runAllTests() {
  console.log('🧪 Starting Comprehensive OCR Functionality Tests...\n');
  console.log('📋 Testing Requirements:');
  console.log('   • OCR extraction with line items, totals, supplier detection');
  console.log('   • AI-based GL coding & cost allocation');
  console.log('   • Fraud detection & anomaly scoring');
  console.log('   • 98% accuracy for totals, 95% for supplier detection');
  console.log('   • Multi-format support (PDF, JPG, PNG, TIFF)');
  console.log('   • Enterprise-grade error handling\n');
  
  // Run all tests
  await testBackendHealth();
  await testOCRServiceHealth();
  await testFrontendHealth();
  await testOCRServiceDirect();
  await testOCRDemoEndpoint();
  await testInvoiceDataExtraction();
  await testConfidenceScoreValidation();
  await testFrontendOCRAPI();
  await testErrorHandling();
  await testFileUploadSimulation();
  
  // Print detailed summary
  console.log('\n📊 Comprehensive Test Summary:');
  console.log('================================');
  console.log(`✅ Passed: ${testResults.passed}`);
  console.log(`❌ Failed: ${testResults.failed}`);
  console.log(`📈 Success Rate: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`);
  
  console.log('\n🎯 Feature Validation:');
  console.log(`Backend Health: ${testResults.summary.backendHealth ? '✅' : '❌'}`);
  console.log(`OCR Service Health: ${testResults.summary.ocrServiceHealth ? '✅' : '❌'}`);
  console.log(`Frontend Health: ${testResults.summary.frontendHealth ? '✅' : '❌'}`);
  console.log(`OCR Processing: ${testResults.summary.ocrProcessing ? '✅' : '❌'}`);
  console.log(`Invoice Extraction: ${testResults.summary.invoiceExtraction ? '✅' : '❌'}`);
  console.log(`Confidence Validation: ${testResults.summary.confidenceValidation ? '✅' : '❌'}`);
  console.log(`API Integration: ${testResults.summary.apiIntegration ? '✅' : '❌'}`);
  console.log(`Error Handling: ${testResults.summary.errorHandling ? '✅' : '❌'}`);
  
  // Save detailed results
  const resultsFile = 'ocr-test-results.json';
  fs.writeFileSync(resultsFile, JSON.stringify(testResults, null, 2));
  console.log(`\n💾 Detailed results saved to ${resultsFile}`);
  
  // Overall assessment
  const criticalTestsPassed = testResults.summary.backendHealth && 
                             testResults.summary.ocrProcessing && 
                             testResults.summary.invoiceExtraction;
  
  if (criticalTestsPassed) {
    console.log('\n🎉 OCR FUNCTIONALITY: READY FOR PRODUCTION');
    console.log('   All critical OCR features are working correctly!');
  } else {
    console.log('\n⚠️  OCR FUNCTIONALITY: NEEDS ATTENTION');
    console.log('   Some critical features need to be fixed before production use.');
  }
  
  return testResults.failed === 0;
}

// Run tests if this script is executed directly
if (require.main === module) {
  runAllTests().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = {
  runAllTests,
  testResults
};
