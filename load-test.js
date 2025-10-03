// K6 Load Test for AI ERP SaaS
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://yourdomain.com';

export function setup() {
  // Login and get auth token
  const loginPayload = JSON.stringify({
    email: 'test@example.com',
    password: 'testpassword'
  });

  const loginResponse = http.post(`${BASE_URL}/api/v1/auth/login`, loginPayload, {
    headers: { 'Content-Type': 'application/json' },
  });

  if (loginResponse.status === 200) {
    const token = loginResponse.json().access_token;
    return { token };
  }

  return { token: null };
}

export default function(data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`,
  };

  // Test 1: Health check
  const healthCheck = http.get(`${BASE_URL}/api/v1/health`);
  check(healthCheck, {
    'health check status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // Test 2: Dashboard data
  const dashboardResponse = http.get(`${BASE_URL}/api/v1/dashboard/overview`, { headers });
  check(dashboardResponse, {
    'dashboard status is 200': (r) => r.status === 200,
    'dashboard response time < 1000ms': (r) => r.timings.duration < 1000,
  }) || errorRate.add(1);

  sleep(2);

  // Test 3: Invoice list
  const invoicesResponse = http.get(`${BASE_URL}/api/v1/invoices?limit=10`, { headers });
  check(invoicesResponse, {
    'invoices status is 200': (r) => r.status === 200,
    'invoices response time < 2000ms': (r) => r.timings.duration < 2000,
  }) || errorRate.add(1);

  sleep(1);

  // Test 4: Vendor list
  const vendorsResponse = http.get(`${BASE_URL}/api/v1/vendors?limit=10`, { headers });
  check(vendorsResponse, {
    'vendors status is 200': (r) => r.status === 200,
    'vendors response time < 1500ms': (r) => r.timings.duration < 1500,
  }) || errorRate.add(1);

  sleep(1);

  // Test 5: Analytics data
  const analyticsResponse = http.get(`${BASE_URL}/api/v1/analytics/summary`, { headers });
  check(analyticsResponse, {
    'analytics status is 200': (r) => r.status === 200,
    'analytics response time < 3000ms': (r) => r.timings.duration < 3000,
  }) || errorRate.add(1);

  sleep(2);

  // Test 6: File upload (simulate)
  const uploadPayload = JSON.stringify({
    filename: 'test-invoice.pdf',
    size: 1024000,
    type: 'application/pdf'
  });

  const uploadResponse = http.post(`${BASE_URL}/api/v1/invoices/upload`, uploadPayload, { headers });
  check(uploadResponse, {
    'upload status is 200 or 400': (r) => r.status === 200 || r.status === 400,
    'upload response time < 5000ms': (r) => r.timings.duration < 5000,
  }) || errorRate.add(1);

  sleep(3);
}

export function teardown(data) {
  // Logout if token exists
  if (data.token) {
    http.post(`${BASE_URL}/api/v1/auth/logout`, {}, {
      headers: { 'Authorization': `Bearer ${data.token}` },
    });
  }
}

