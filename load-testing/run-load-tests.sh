#!/bin/bash

# Load Testing Runner Script for AI ERP SaaS Application
# Runs comprehensive load tests using K6

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$SCRIPT_DIR/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create results directory
mkdir -p "$RESULTS_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if K6 is installed
check_k6() {
    if ! command -v k6 &> /dev/null; then
        print_error "K6 is not installed. Please install it first:"
        echo "  - macOS: brew install k6"
        echo "  - Linux: https://k6.io/docs/getting-started/installation/"
        echo "  - Windows: choco install k6"
        exit 1
    fi
    
    print_success "K6 is installed: $(k6 version)"
}

# Function to check if the application is running
check_app() {
    print_status "Checking if application is running..."
    
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Backend API is running"
    else
        print_error "Backend API is not running. Please start the application first:"
        echo "  cd $PROJECT_ROOT"
        echo "  docker-compose -f docker-compose.dev.yml up -d"
        exit 1
    fi
}

# Function to run a specific load test
run_test() {
    local test_name="$1"
    local script_file="$2"
    local description="$3"
    
    print_status "Running $test_name test..."
    print_status "Description: $description"
    
    local result_file="$RESULTS_DIR/${test_name}_${TIMESTAMP}.json"
    local summary_file="$RESULTS_DIR/${test_name}_${TIMESTAMP}_summary.txt"
    
    # Run the test
    if k6 run --out json="$result_file" "$script_file" > "$summary_file" 2>&1; then
        print_success "$test_name test completed successfully"
        
        # Extract key metrics from summary
        echo ""
        echo "=== $test_name Test Results ==="
        grep -E "(checks|http_req_duration|http_req_failed|iterations)" "$summary_file" | head -10
        echo ""
        
        return 0
    else
        print_error "$test_name test failed"
        echo "Check the summary file for details: $summary_file"
        return 1
    fi
}

# Function to run all load tests
run_all_tests() {
    print_status "Starting comprehensive load testing suite..."
    echo "Results will be saved to: $RESULTS_DIR"
    echo ""
    
    local tests=(
        "ocr_processing:k6-ocr-load-test.js:OCR Processing Load Test"
        "approver_workflow:k6-approver-load-test.js:Approver Workflow Load Test"
        "resilience_testing:k6-resilience-test.js:Resilience Testing"
    )
    
    local passed=0
    local failed=0
    
    for test in "${tests[@]}"; do
        IFS=':' read -r test_name script_file description <<< "$test"
        
        if run_test "$test_name" "$script_file" "$description"; then
            ((passed++))
        else
            ((failed++))
        fi
        
        echo "----------------------------------------"
    done
    
    # Summary
    echo ""
    print_status "Load Testing Summary:"
    print_success "Passed: $passed"
    if [ $failed -gt 0 ]; then
        print_error "Failed: $failed"
    else
        print_success "Failed: $failed"
    fi
    
    echo ""
    print_status "Results saved to: $RESULTS_DIR"
    print_status "View detailed results:"
    echo "  - JSON results: $RESULTS_DIR/*_${TIMESTAMP}.json"
    echo "  - Summary reports: $RESULTS_DIR/*_${TIMESTAMP}_summary.txt"
}

# Function to run a specific test
run_specific_test() {
    local test_name="$1"
    
    case "$test_name" in
        "ocr")
            run_test "ocr_processing" "k6-ocr-load-test.js" "OCR Processing Load Test"
            ;;
        "approver")
            run_test "approver_workflow" "k6-approver-load-test.js" "Approver Workflow Load Test"
            ;;
        "resilience")
            run_test "resilience_testing" "k6-resilience-test.js" "Resilience Testing"
            ;;
        *)
            print_error "Unknown test: $test_name"
            echo "Available tests: ocr, approver, resilience"
            exit 1
            ;;
    esac
}

# Function to show help
show_help() {
    echo "Load Testing Runner for AI ERP SaaS Application"
    echo ""
    echo "Usage: $0 [OPTIONS] [TEST_NAME]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -a, --all      Run all load tests (default)"
    echo "  -c, --check    Check prerequisites only"
    echo ""
    echo "Test Names:"
    echo "  ocr           Run OCR processing load test"
    echo "  approver      Run approver workflow load test"
    echo "  resilience    Run resilience testing"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 --all              # Run all tests"
    echo "  $0 ocr                # Run OCR test only"
    echo "  $0 --check            # Check prerequisites only"
}

# Main script logic
main() {
    # Parse command line arguments
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--check)
            check_k6
            check_app
            print_success "All prerequisites are met"
            exit 0
            ;;
        -a|--all|"")
            check_k6
            check_app
            run_all_tests
            ;;
        *)
            check_k6
            check_app
            run_specific_test "$1"
            ;;
    esac
}

# Run main function
main "$@"
