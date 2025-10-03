/**
 * K6 Resilience Test for AI ERP SaaS Application
 * Tests system resilience under failure conditions and recovery
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const resilienceSuccessRate = new Rate('resilience_success_rate');
const recoveryTime = new Trend('recovery_time');
const failureCount = new Counter('failure_count');
const retrySuccessRate = new Rate('retry_success_rate');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Normal load
    { duration: '1m', target: 50 },   // High load
    { duration: '2m', target: 10 },   // Back to normal
    { duration: '1m', target: 100 },  // Stress test
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'], // 95% of requests must complete below 5s
    http_req_failed: ['rate<0.2'],     // Error rate must be below 20% (higher due to resilience testing)
    resilience_success_rate: ['rate>0.8'], // 80% success rate during resilience testing
    recovery_time: ['p(95)<10000'], // 95% of recoveries must complete below 10s
  },
};

// Test scenarios
const scenarios = [
  'normal_operation',
  'high_load',
  'service_restart',
  'database_connection_loss',
  'network_timeout',
  'memory_pressure',
  'concurrent_failures'
];

let authToken = '';
let currentScenario = 'normal_operation';

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
  
  // Determine current scenario based on test stage
  const stage = __ENV.STAGE || 'normal';
  currentScenario = determineScenario(stage);
  
  // Execute resilience test based on scenario
  switch (currentScenario) {
    case 'normal_operation':
      testNormalOperation(headers);
      break;
    case 'high_load':
      testHighLoad(headers);
      break;
    case 'service_restart':
      testServiceRestart(headers);
      break;
    case 'database_connection_loss':
      testDatabaseConnectionLoss(headers);
      break;
    case 'network_timeout':
      testNetworkTimeout(headers);
      break;
    case 'memory_pressure':
      testMemoryPressure(headers);
      break;
    case 'concurrent_failures':
      testConcurrentFailures(headers);
      break;
  }
  
  sleep(1);
}

function determineScenario(stage) {
  const scenarios = [
    'normal_operation',
    'high_load', 
    'service_restart',
    'database_connection_loss',
    'network_timeout',
    'memory_pressure',
    'concurrent_failures'
  ];
  
  return scenarios[Math.floor(Math.random() * scenarios.length)];
}

function testNormalOperation(headers) {
  // Test normal API operations
  const healthResponse = http.get('http://localhost:8000/health', { headers });
  
  const success = check(healthResponse, {
    'health check successful': (r) => r.status === 200,
    'response time < 100ms': (r) => r.timings.duration < 100,
  });
  
  resilienceSuccessRate.add(success);
}

function testHighLoad(headers) {
  // Test under high load conditions
  const startTime = Date.now();
  
  // Concurrent requests
  const requests = [
    http.get('http://localhost:8000/api/v1/invoices', { headers }),
    http.get('http://localhost:8000/api/v1/analytics/dashboard', { headers }),
    http.post('http://localhost:8000/api/v1/ocr/process', {
      filename: 'test.pdf',
      content: 'base64-content'
    }, { headers }),
  ];
  
  const success = check(requests[0], {
    'high load request successful': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });
  
  const recoveryTime = Date.now() - startTime;
  recoveryTime.add(recoveryTime);
  
  resilienceSuccessRate.add(success);
}

function testServiceRestart(headers) {
  // Test behavior during service restart
  const startTime = Date.now();
  let retryCount = 0;
  const maxRetries = 5;
  let success = false;
  
  while (retryCount < maxRetries && !success) {
    const response = http.get('http://localhost:8000/health', { 
      headers,
      timeout: '5s'
    });
    
    if (response.status === 200) {
      success = true;
    } else {
      retryCount++;
      sleep(2); // Wait 2 seconds before retry
    }
  }
  
  const recoveryTime = Date.now() - startTime;
  recoveryTime.add(recoveryTime);
  
  const retrySuccess = check({ status: success ? 200 : 500 }, {
    'service restart recovery': (r) => r.status === 200,
    'recovery time < 30s': () => recoveryTime < 30000,
  });
  
  retrySuccessRate.add(retrySuccess);
  resilienceSuccessRate.add(success);
}

function testDatabaseConnectionLoss(headers) {
  // Test behavior when database is unavailable
  const response = http.get('http://localhost:8000/api/v1/invoices', { 
    headers,
    timeout: '10s'
  });
  
  const success = check(response, {
    'database connection loss handled': (r) => r.status === 200 || r.status === 503,
    'graceful degradation': (r) => r.status !== 500,
  });
  
  resilienceSuccessRate.add(success);
}

function testNetworkTimeout(headers) {
  // Test behavior with network timeouts
  const response = http.get('http://localhost:8000/api/v1/analytics/dashboard', { 
    headers,
    timeout: '2s'
  });
  
  const success = check(response, {
    'timeout handled gracefully': (r) => r.status === 200 || r.status === 408,
    'no server error on timeout': (r) => r.status !== 500,
  });
  
  resilienceSuccessRate.add(success);
}

function testMemoryPressure(headers) {
  // Test behavior under memory pressure
  const response = http.post('http://localhost:8000/api/v1/ocr/process', {
    filename: 'large-invoice.pdf',
    content: 'x'.repeat(1000000) // Large content to simulate memory pressure
  }, { 
    headers,
    timeout: '15s'
  });
  
  const success = check(response, {
    'memory pressure handled': (r) => r.status === 200 || r.status === 413,
    'no memory error': (r) => r.status !== 500,
  });
  
  resilienceSuccessRate.add(success);
}

function testConcurrentFailures(headers) {
  // Test behavior with multiple concurrent failures
  const startTime = Date.now();
  
  // Simulate multiple concurrent operations that might fail
  const operations = [
    () => http.get('http://localhost:8000/api/v1/invoices', { headers }),
    () => http.post('http://localhost:8000/api/v1/ocr/process', {
      filename: 'test.pdf',
      content: 'base64-content'
    }, { headers }),
    () => http.get('http://localhost:8000/api/v1/analytics/dashboard', { headers }),
    () => http.post('http://localhost:8000/api/v1/invoices', {
      invoice_number: 'TEST-001',
      supplier_name: 'Test Supplier',
      total_amount: 100.00
    }, { headers }),
  ];
  
  let successCount = 0;
  const totalOperations = operations.length;
  
  for (const operation of operations) {
    try {
      const response = operation();
      if (response.status >= 200 && response.status < 500) {
        successCount++;
      }
    } catch (error) {
      failureCount.add(1);
    }
  }
  
  const recoveryTime = Date.now() - startTime;
  recoveryTime.add(recoveryTime);
  
  const success = check({ successCount, totalOperations }, {
    'concurrent failures handled': (r) => r.successCount > 0,
    'partial success acceptable': (r) => r.successCount >= r.totalOperations * 0.5,
  });
  
  resilienceSuccessRate.add(success);
}

export function teardown(data) {
  console.log('Resilience Test completed');
  console.log(`Final scenario: ${currentScenario}`);
}
