# Load Testing Infrastructure for AI ERP SaaS Application

This directory contains comprehensive load testing infrastructure using K6 for the AI ERP SaaS application.

## Overview

The load testing suite includes:
- **OCR Processing Load Test**: Tests concurrent invoice uploads and OCR processing (1000 invoices/minute)
- **Approver Workflow Load Test**: Tests 200 concurrent approver reads and approval actions
- **Resilience Testing**: Tests system resilience under failure conditions and recovery

## Prerequisites

### Option 1: Local K6 Installation
```bash
# macOS
brew install k6

# Linux
curl https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz -L | tar xvz --strip-components 1

# Windows
choco install k6
```

### Option 2: Docker-based Testing
```bash
# Build the load testing image
docker build -t ai-erp-load-test .

# Run tests using Docker Compose
docker-compose up
```

## Running Load Tests

### Quick Start
```bash
# Run all load tests
./run-load-tests.sh

# Run specific test
./run-load-tests.sh ocr
./run-load-tests.sh approver
./run-load-tests.sh resilience

# Check prerequisites only
./run-load-tests.sh --check
```

### Manual K6 Execution
```bash
# OCR Processing Test
k6 run k6-ocr-load-test.js

# Approver Workflow Test
k6 run k6-approver-load-test.js

# Resilience Test
k6 run k6-resilience-test.js
```

## Test Scenarios

### 1. OCR Processing Load Test (`k6-ocr-load-test.js`)

**Purpose**: Tests concurrent invoice uploads and OCR processing capabilities.

**Load Pattern**:
- Ramp up to 10 users over 2 minutes
- Ramp up to 50 users over 5 minutes
- Ramp up to 100 users over 10 minutes
- Ramp down to 0 users over 5 minutes

**Key Metrics**:
- OCR success rate > 90%
- OCR processing time < 5 seconds (95th percentile)
- Upload response time < 2 seconds (95th percentile)
- Error rate < 10%

**Test Flow**:
1. Upload invoice for OCR processing
2. Poll for OCR completion
3. Verify OCR results accuracy
4. Create invoice from OCR data

### 2. Approver Workflow Load Test (`k6-approver-load-test.js`)

**Purpose**: Tests concurrent approver reads and approval actions.

**Load Pattern**:
- Ramp up to 20 approvers over 1 minute
- Ramp up to 50 approvers over 5 minutes
- Ramp up to 100 approvers over 10 minutes
- Ramp down to 0 approvers over 5 minutes

**Key Metrics**:
- Approval success rate > 95%
- Approval processing time < 2 seconds (95th percentile)
- List response time < 500ms (95th percentile)
- Error rate < 5%

**Test Flow**:
1. Get pending invoices list
2. Get specific invoice details
3. Approve or reject invoice (80% approve, 20% reject)
4. Verify status update
5. Get approval history

### 3. Resilience Testing (`k6-resilience-test.js`)

**Purpose**: Tests system resilience under failure conditions and recovery.

**Load Pattern**:
- Normal load (10 users) for 2 minutes
- High load (50 users) for 1 minute
- Back to normal (10 users) for 2 minutes
- Stress test (100 users) for 1 minute
- Ramp down to 0 users over 2 minutes

**Key Metrics**:
- Resilience success rate > 80%
- Recovery time < 10 seconds (95th percentile)
- Error rate < 20% (higher due to resilience testing)

**Test Scenarios**:
- Normal operation
- High load conditions
- Service restart simulation
- Database connection loss
- Network timeout handling
- Memory pressure
- Concurrent failures

## Configuration

### K6 Configuration (`k6-config.json`)
Contains test configurations, thresholds, and environment settings.

### Environment Variables
```bash
export K6_BASE_URL=http://localhost:8000
export K6_API_VERSION=v1
export K6_TIMEOUT=30s
export K6_RETRIES=3
export K6_RETRY_DELAY=2s
```

## Results and Monitoring

### Output Formats
- **JSON**: Detailed metrics and results
- **Console**: Real-time progress and summary
- **Summary**: Text-based summary report

### Key Metrics Tracked
- HTTP request duration
- HTTP request failure rate
- Custom application metrics
- Resource utilization
- Error patterns

### Results Location
```
load-testing/
├── results/
│   ├── ocr_processing_YYYYMMDD_HHMMSS.json
│   ├── approver_workflow_YYYYMMDD_HHMMSS.json
│   ├── resilience_testing_YYYYMMDD_HHMMSS.json
│   └── *_summary.txt
```

## Performance Thresholds

### OCR Processing
- **Throughput**: 1000 invoices/minute
- **Response Time**: < 2 seconds (95th percentile)
- **Success Rate**: > 90%
- **Processing Time**: < 5 seconds (95th percentile)

### Approver Workflow
- **Concurrent Users**: 200 approvers
- **Response Time**: < 1 second (95th percentile)
- **Success Rate**: > 95%
- **Processing Time**: < 2 seconds (95th percentile)

### Resilience Testing
- **Recovery Time**: < 10 seconds (95th percentile)
- **Success Rate**: > 80% (under failure conditions)
- **Error Rate**: < 20% (acceptable during resilience testing)

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the application is running
   - Check if the API is accessible at the configured URL

2. **Authentication Failures**
   - Verify test user credentials
   - Check if the auth endpoint is working

3. **High Error Rates**
   - Check application logs
   - Verify database connectivity
   - Monitor resource utilization

4. **Timeout Errors**
   - Increase timeout values in configuration
   - Check network connectivity
   - Monitor application performance

### Debug Mode
```bash
# Run with verbose output
k6 run --verbose k6-ocr-load-test.js

# Run with debug logging
k6 run --log-level=debug k6-ocr-load-test.js
```

## Continuous Integration

### GitHub Actions Integration
The load tests can be integrated into CI/CD pipelines:

```yaml
- name: Run Load Tests
  run: |
    cd load-testing
    ./run-load-tests.sh
```

### Docker Integration
```yaml
- name: Run Load Tests with Docker
  run: |
    cd load-testing
    docker-compose up --abort-on-container-exit
```

## Best Practices

1. **Test Environment**: Use a dedicated test environment that mirrors production
2. **Data Preparation**: Ensure test data is available and consistent
3. **Monitoring**: Monitor system resources during testing
4. **Gradual Ramp-up**: Use gradual load increase to identify breaking points
5. **Baseline Establishment**: Establish performance baselines before optimization
6. **Regular Testing**: Run load tests regularly to catch performance regressions

## Contributing

When adding new load tests:
1. Follow the existing naming convention
2. Include comprehensive documentation
3. Set appropriate thresholds
4. Test with various load patterns
5. Update this README with new test information
