/**
 * K6 Load Test for Invoice Approval Workflow
 * Tests concurrent approver reads and approval actions
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const approvalSuccessRate = new Rate('approval_success_rate');
const approvalProcessingTime = new Trend('approval_processing_time');
const approvalErrorCount = new Counter('approval_error_count');
const invoiceListTime = new Trend('invoice_list_time');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 20 },   // Ramp up to 20 approvers
    { duration: '5m', target: 50 },   // Ramp up to 50 approvers
    { duration: '10m', target: 100 }, // Ramp up to 100 approvers
    { duration: '5m', target: 0 },    // Ramp down to 0 approvers
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests must complete below 1s
    http_req_failed: ['rate<0.05'],    // Error rate must be below 5%
    approval_success_rate: ['rate>0.95'], // Approval success rate must be above 95%
    approval_processing_time: ['p(95)<2000'], // 95% of approvals must complete below 2s
  },
};

// Test data
const approverCredentials = [
  { email: 'approver1@example.com', password: 'password123' },
  { email: 'approver2@example.com', password: 'password123' },
  { email: 'approver3@example.com', password: 'password123' },
  { email: 'approver4@example.com', password: 'password123' },
  { email: 'approver5@example.com', password: 'password123' },
];

let authTokens = {};

export function setup() {
  // Login multiple approvers
  const tokens = {};
  
  for (const cred of approverCredentials) {
    const loginResponse = http.post('http://localhost:8000/api/v1/auth/login', {
      email: cred.email,
      password: cred.password
    });
    
    if (loginResponse.status === 200) {
      const loginData = JSON.parse(loginResponse.body);
      tokens[cred.email] = loginData.access_token;
    }
  }
  
  return { tokens };
}

export default function(data) {
  const tokens = data.tokens;
  const approverEmails = Object.keys(tokens);
  const randomApprover = approverEmails[Math.floor(Math.random() * approverEmails.length)];
  const token = tokens[randomApprover];
  
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
  
  // Test 1: Get pending invoices list
  const listStart = Date.now();
  const listResponse = http.get('http://localhost:8000/api/v1/invoices?status=pending_approval&limit=20', { headers });
  const listTime = Date.now() - listStart;
  invoiceListTime.add(listTime);
  
  const listSuccess = check(listResponse, {
    'invoice list successful': (r) => r.status === 200,
    'list response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  if (!listSuccess) {
    approvalErrorCount.add(1);
    return;
  }
  
  const invoices = JSON.parse(listResponse.body).invoices;
  
  if (invoices.length === 0) {
    // No pending invoices, wait and try again
    sleep(2);
    return;
  }
  
  // Test 2: Get specific invoice details
  const randomInvoice = invoices[Math.floor(Math.random() * invoices.length)];
  const detailResponse = http.get(`http://localhost:8000/api/v1/invoices/${randomInvoice.id}`, { headers });
  
  const detailSuccess = check(detailResponse, {
    'invoice detail successful': (r) => r.status === 200,
    'detail response time < 300ms': (r) => r.timings.duration < 300,
  });
  
  if (!detailSuccess) {
    approvalErrorCount.add(1);
    return;
  }
  
  // Test 3: Approve or reject invoice (80% approve, 20% reject)
  const shouldApprove = Math.random() < 0.8;
  const approvalStart = Date.now();
  
  let approvalResponse;
  if (shouldApprove) {
    approvalResponse = http.post(
      `http://localhost:8000/api/v1/invoices/${randomInvoice.id}/approve`,
      {},
      { headers }
    );
  } else {
    approvalResponse = http.post(
      `http://localhost:8000/api/v1/invoices/${randomInvoice.id}/reject`,
      { reason: 'Test rejection for load testing' },
      { headers }
    );
  }
  
  const approvalTime = Date.now() - approvalStart;
  approvalProcessingTime.add(approvalTime);
  
  const approvalSuccess = check(approvalResponse, {
    'approval action successful': (r) => r.status === 200,
    'approval response time < 1s': (r) => r.timings.duration < 1000,
  });
  
  approvalSuccessRate.add(approvalSuccess);
  
  if (!approvalSuccess) {
    approvalErrorCount.add(1);
  }
  
  // Test 4: Get updated invoice status
  const statusResponse = http.get(`http://localhost:8000/api/v1/invoices/${randomInvoice.id}`, { headers });
  
  check(statusResponse, {
    'status check successful': (r) => r.status === 200,
    'status updated correctly': (r) => {
      const invoice = JSON.parse(r.body);
      return shouldApprove ? invoice.status === 'approved' : invoice.status === 'rejected';
    },
  });
  
  // Test 5: Get approval history
  const historyResponse = http.get(`http://localhost:8000/api/v1/invoices/${randomInvoice.id}/history`, { headers });
  
  check(historyResponse, {
    'history retrieval successful': (r) => r.status === 200,
    'history response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  // Random sleep between 0.5-2 seconds
  sleep(Math.random() * 1.5 + 0.5);
}

export function teardown(data) {
  console.log('Approver Load Test completed');
}
