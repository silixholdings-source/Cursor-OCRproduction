#!/usr/bin/env python3
"""
Test runner script for the FastAPI backend
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} failed with return code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True

def main():
    parser = argparse.ArgumentParser(description="Run tests for the FastAPI backend")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-n", type=int, help="Number of parallel workers")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["OCR_SERVICE_URL"] = "http://localhost:8001"
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    if args.parallel:
        pytest_cmd.extend(["-n", str(args.parallel)])
    
    if args.coverage:
        pytest_cmd.extend(["--cov=src", "--cov-report=term-missing"])
    
    if args.html:
        pytest_cmd.extend(["--cov-report=html:htmlcov"])
    
    # Add test markers
    if args.unit:
        pytest_cmd.extend(["-m", "unit"])
    elif args.integration:
        pytest_cmd.extend(["-m", "integration"])
    elif args.performance:
        pytest_cmd.extend(["-m", "performance"])
    elif not args.all:
        # Default to unit and integration tests
        pytest_cmd.extend(["-m", "unit or integration"])
    
    # Add test directory
    pytest_cmd.append("tests/")
    
    # Convert to string for subprocess
    command = " ".join(pytest_cmd)
    
    # Run tests
    success = run_command(command, "Running tests")
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()