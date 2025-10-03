#!/usr/bin/env python3
"""
Simple Docker test runner for immediate testing
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {command}")
        return None
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def test_docker_availability():
    """Test if Docker is available"""
    print("=== Testing Docker Availability ===")
    
    # Check Docker
    docker_result = run_command("docker --version")
    if not docker_result or docker_result.returncode != 0:
        print("- Docker is not available")
        return False
    print(f"+ Docker: {docker_result.stdout.strip()}")
    
    # Check Docker Compose
    compose_result = run_command("docker-compose --version")
    if not compose_result or compose_result.returncode != 0:
        print("- Docker Compose is not available")
        return False
    print(f"+ Docker Compose: {compose_result.stdout.strip()}")
    
    return True

def test_services_startup():
    """Test if we can start the test services"""
    print("\n=== Testing Services Startup ===")
    
    project_root = Path(__file__).parent.parent
    
    # Start test services
    start_result = run_command(
        "docker-compose -f docker-compose.test.yml up -d postgres-test redis-test",
        cwd=project_root
    )
    
    if not start_result or start_result.returncode != 0:
        print("- Failed to start test services")
        print(f"Error: {start_result.stderr if start_result else 'No output'}")
        return False
    
    print("+ Test services started successfully")
    
    # Wait a bit for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(10)
    
    # Check service status
    status_result = run_command(
        "docker-compose -f docker-compose.test.yml ps",
        cwd=project_root
    )
    
    if status_result:
        print("Service status:")
        print(status_result.stdout)
    
    return True

def test_ocr_service():
    """Test OCR service in Docker"""
    print("\n=== Testing OCR Service ===")
    
    project_root = Path(__file__).parent.parent
    
    # Build OCR service
    build_result = run_command(
        "docker build -t ai-erp-ocr-test ./ocr-service",
        cwd=project_root
    )
    
    if not build_result or build_result.returncode != 0:
        print("- Failed to build OCR service")
        print(f"Error: {build_result.stderr if build_result else 'No output'}")
        return False
    
    print("+ OCR service built successfully")
    
    # Run OCR service test
    run_result = run_command(
        "docker run --rm -p 8002:8001 ai-erp-ocr-test python -c \"print('OCR service test')\"",
        cwd=project_root
    )
    
    if not run_result or run_result.returncode != 0:
        print("- Failed to run OCR service test")
        print(f"Error: {run_result.stderr if run_result else 'No output'}")
        return False
    
    print("+ OCR service test passed")
    return True

def test_backend_in_docker():
    """Test backend in Docker"""
    print("\n=== Testing Backend in Docker ===")
    
    project_root = Path(__file__).parent.parent
    
    # Build backend
    build_result = run_command(
        "docker build -t ai-erp-backend-test ./backend",
        cwd=project_root
    )
    
    if not build_result or build_result.returncode != 0:
        print("- Failed to build backend")
        print(f"Error: {build_result.stderr if build_result else 'No output'}")
        return False
    
    print("+ Backend built successfully")
    
    # Run backend test
    run_result = run_command(
        "docker run --rm ai-erp-backend-test python test_ocr_standalone.py",
        cwd=project_root
    )
    
    if not run_result or run_result.returncode != 0:
        print("- Failed to run backend test")
        print(f"Error: {run_result.stderr if run_result else 'No output'}")
        return False
    
    print("+ Backend test passed")
    return True

def cleanup_services():
    """Clean up test services"""
    print("\n=== Cleaning Up ===")
    
    project_root = Path(__file__).parent.parent
    
    # Stop services
    stop_result = run_command(
        "docker-compose -f docker-compose.test.yml down -v",
        cwd=project_root
    )
    
    if stop_result and stop_result.returncode == 0:
        print("+ Services cleaned up")
    else:
        print("- Cleanup may have failed")
    
    # Remove test images
    run_command("docker rmi ai-erp-ocr-test ai-erp-backend-test", cwd=project_root)

def main():
    """Main test runner"""
    print("Docker Test Suite")
    print("=" * 30)
    
    tests = [
        ("Docker Availability", test_docker_availability),
        ("Services Startup", test_services_startup),
        ("OCR Service", test_ocr_service),
        ("Backend in Docker", test_backend_in_docker),
    ]
    
    passed = 0
    total = len(tests)
    
    try:
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            if test_func():
                passed += 1
                print(f"+ {test_name} PASSED")
            else:
                print(f"- {test_name} FAILED")
    finally:
        cleanup_services()
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("+ ALL DOCKER TESTS PASSED!")
        return True
    else:
        print("- SOME DOCKER TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
