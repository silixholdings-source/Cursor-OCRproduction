#!/usr/bin/env python3
"""
Development Environment Setup Script for AI ERP SaaS Application
Automatically sets up the complete development environment with Docker
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

class DevSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.setup_results = {}
        
    def run_command(self, command: str, cwd: str = None) -> Tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 5 minutes"
        except Exception as e:
            return -1, "", str(e)
    
    def check_docker(self) -> bool:
        """Check if Docker is available and running"""
        print("🔍 Checking Docker availability...")
        
        # Check Docker version
        exit_code, stdout, stderr = self.run_command("docker --version")
        if exit_code != 0:
            print("❌ Docker not found. Please install Docker Desktop first.")
            return False
        
        print(f"✅ Docker found: {stdout.strip()}")
        
        # Check Docker Compose
        exit_code, stdout, stderr = self.run_command("docker-compose --version")
        if exit_code != 0:
            print("❌ Docker Compose not found.")
            return False
        
        print(f"✅ Docker Compose found: {stdout.strip()}")
        
        # Check if Docker daemon is running
        exit_code, stdout, stderr = self.run_command("docker info")
        if exit_code != 0:
            print("❌ Docker daemon not running. Please start Docker Desktop.")
            return False
        
        print("✅ Docker daemon is running")
        return True
    
    def build_images(self) -> bool:
        """Build all Docker images"""
        print("\n🔨 Building Docker images...")
        
        cmd = "docker-compose -f docker-compose.dev.yml build --no-cache"
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            print("✅ Docker images built successfully")
            self.setup_results['build'] = {'status': 'SUCCESS', 'output': stdout}
            return True
        else:
            print("❌ Failed to build Docker images")
            print(f"Error: {stderr}")
            self.setup_results['build'] = {'status': 'FAILED', 'output': stdout, 'error': stderr}
            return False
    
    def start_infrastructure(self) -> bool:
        """Start infrastructure services (PostgreSQL, Redis)"""
        print("\n🚀 Starting infrastructure services...")
        
        cmd = "docker-compose -f docker-compose.dev.yml up -d postgres redis"
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            print("✅ Infrastructure services started")
            self.setup_results['infrastructure'] = {'status': 'SUCCESS', 'output': stdout}
            return True
        else:
            print("❌ Failed to start infrastructure services")
            print(f"Error: {stderr}")
            self.setup_results['infrastructure'] = {'status': 'FAILED', 'output': stdout, 'error': stderr}
            return False
    
    def wait_for_services(self) -> bool:
        """Wait for services to be ready"""
        print("\n⏳ Waiting for services to be ready...")
        
        # Wait for PostgreSQL
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            exit_code, stdout, stderr = self.run_command(
                "docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres"
            )
            if exit_code == 0:
                print("✅ PostgreSQL is ready")
                break
            attempt += 1
            print(f"  Waiting for PostgreSQL... (attempt {attempt}/{max_attempts})")
            time.sleep(2)
        
        if attempt >= max_attempts:
            print("❌ PostgreSQL failed to become ready")
            return False
        
        # Wait for Redis
        attempt = 0
        while attempt < max_attempts:
            exit_code, stdout, stderr = self.run_command(
                "docker-compose -f docker-compose.dev.yml exec redis redis-cli ping"
            )
            if exit_code == 0 and "PONG" in stdout:
                print("✅ Redis is ready")
                break
            attempt += 1
            print(f"  Waiting for Redis... (attempt {attempt}/{max_attempts})")
            time.sleep(2)
        
        if attempt >= max_attempts:
            print("❌ Redis failed to become ready")
            return False
        
        return True
    
    def run_migrations(self) -> bool:
        """Run database migrations"""
        print("\n🗄️ Running database migrations...")
        
        cmd = "docker-compose -f docker-compose.dev.yml run --rm backend python -m alembic upgrade head"
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            print("✅ Database migrations completed")
            self.setup_results['migrations'] = {'status': 'SUCCESS', 'output': stdout}
            return True
        else:
            print("❌ Database migrations failed")
            print(f"Error: {stderr}")
            self.setup_results['migrations'] = {'status': 'FAILED', 'output': stdout, 'error': stderr}
            return False
    
    def create_tables(self) -> bool:
        """Create database tables"""
        print("\n📋 Creating database tables...")
        
        cmd = """docker-compose -f docker-compose.dev.yml run --rm backend python -c "
from src.core.database import engine
from src.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"
"""
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            print("✅ Database tables created")
            self.setup_results['tables'] = {'status': 'SUCCESS', 'output': stdout}
            return True
        else:
            print("❌ Failed to create database tables")
            print(f"Error: {stderr}")
            self.setup_results['tables'] = {'status': 'FAILED', 'output': stdout, 'error': stderr}
            return False
    
    def seed_test_data(self) -> bool:
        """Seed database with test data"""
        print("\n🌱 Seeding test data...")
        
        # Try to seed test data if the function exists
        cmd = """docker-compose -f docker-compose.dev.yml run --rm backend python -c "
try:
    from src.services.audit import seed_test_data
    seed_test_data()
    print('Test data seeded successfully')
except ImportError:
    print('Seed function not available, skipping...')
except Exception as e:
    print(f'Error seeding data: {e}')
"
"""
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            print("✅ Test data seeded (or function not available)")
            self.setup_results['seeding'] = {'status': 'SUCCESS', 'output': stdout}
            return True
        else:
            print("⚠️ Seeding encountered issues (continuing anyway)")
            self.setup_results['seeding'] = {'status': 'WARNING', 'output': stdout, 'error': stderr}
            return True  # Don't fail setup for seeding issues
    
    def run_health_checks(self) -> bool:
        """Run health checks on all services"""
        print("\n🏥 Running health checks...")
        
        # Check backend health
        print("  Checking backend API...")
        exit_code, stdout, stderr = self.run_command("curl -f http://localhost:8000/health")
        if exit_code == 0:
            print("    ✅ Backend API is healthy")
        else:
            print("    ❌ Backend API health check failed")
            return False
        
        # Check database health
        print("  Checking database...")
        exit_code, stdout, stderr = self.run_command(
            "docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres"
        )
        if exit_code == 0:
            print("    ✅ Database is healthy")
        else:
            print("    ❌ Database health check failed")
            return False
        
        # Check Redis health
        print("  Checking Redis...")
        exit_code, stdout, stderr = self.run_command(
            "docker-compose -f docker-compose.dev.yml exec redis redis-cli ping"
        )
        if exit_code == 0 and "PONG" in stdout:
            print("    ✅ Redis is healthy")
        else:
            print("    ❌ Redis health check failed")
            return False
        
        print("✅ All health checks passed")
        self.setup_results['health_checks'] = {'status': 'SUCCESS', 'output': 'All services healthy'}
        return True
    
    def start_application(self) -> bool:
        """Start the main application services"""
        print("\n🚀 Starting application services...")
        
        cmd = "docker-compose -f docker-compose.dev.yml up -d backend web worker"
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            print("✅ Application services started")
            self.setup_results['application'] = {'status': 'SUCCESS', 'output': stdout}
            return True
        else:
            print("❌ Failed to start application services")
            print(f"Error: {stderr}")
            self.setup_results['application'] = {'status': 'FAILED', 'output': stdout, 'error': stderr}
            return False
    
    def run_initial_tests(self) -> bool:
        """Run initial smoke tests"""
        print("\n🧪 Running initial smoke tests...")
        
        # Wait a bit for services to fully start
        print("  Waiting for services to fully start...")
        time.sleep(10)
        
        # Run basic health check tests
        cmd = "docker-compose -f docker-compose.dev.yml run --rm test-runner pytest tests/unit/test_health.py -v"
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            print("✅ Initial tests passed")
            self.setup_results['initial_tests'] = {'status': 'SUCCESS', 'output': stdout}
            return True
        else:
            print("❌ Initial tests failed")
            print(f"Error: {stderr}")
            self.setup_results['initial_tests'] = {'status': 'FAILED', 'output': stdout, 'error': stderr}
            return False
    
    def generate_setup_report(self) -> str:
        """Generate setup completion report"""
        report = f"""
# AI ERP SaaS Development Environment Setup Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Setup Summary
"""
        
        successful = sum(1 for result in self.setup_results.values() if result.get('status') == 'SUCCESS')
        failed = sum(1 for result in self.setup_results.values() if result.get('status') == 'FAILED')
        warnings = sum(1 for result in self.setup_results.values() if result.get('status') == 'WARNING')
        total = len(self.setup_results)
        
        report += f"""
- Total Steps: {total}
- Successful: {successful}
- Failed: {failed}
- Warnings: {warnings}
- Success Rate: {(successful/total*100):.1f}%

## Detailed Results
"""
        
        for step_name, result in self.setup_results.items():
            status_emoji = {
                'SUCCESS': '[SUCCESS]',
                'FAILED': '[FAILED]',
                'WARNING': '[WARNING]'
            }.get(result.get('status'), '[UNKNOWN]')
            
            report += f"\n### {step_name.replace('_', ' ').title()} {status_emoji}\n"
            report += f"Status: {result.get('status')}\n"
            
            if result.get('error'):
                report += f"Error: {result.get('error')}\n"
        
        report += f"""

## Next Steps
"""
        
        if failed == 0:
            report += """
Development environment setup completed successfully!

You can now:
1. Access the backend API at: http://localhost:8000
2. View API documentation at: http://localhost:8000/docs
3. Access the web frontend at: http://localhost:3000
4. Run tests with: make test
5. View logs with: make logs
6. Stop services with: make stop

The system is ready for development and testing!
"""
        else:
            report += """
Setup encountered some issues. Please review the failed steps above.

You can:
1. Check logs with: make logs
2. Restart services with: make restart
3. Run specific tests to debug issues
4. Contact the development team for assistance

Please resolve the issues before proceeding with development.
"""
        
        return report
    
    def setup_development_environment(self) -> bool:
        """Complete development environment setup"""
        print("🚀 Setting up AI ERP SaaS Development Environment")
        print("=" * 70)
        
        if not self.check_docker():
            return False
        
        setup_steps = [
            ("Building Docker Images", self.build_images),
            ("Starting Infrastructure", self.start_infrastructure),
            ("Waiting for Services", self.wait_for_services),
            ("Running Migrations", self.run_migrations),
            ("Creating Tables", self.create_tables),
            ("Seeding Test Data", self.seed_test_data),
            ("Health Checks", self.run_health_checks),
            ("Starting Application", self.start_application),
            ("Initial Tests", self.run_initial_tests)
        ]
        
        all_successful = True
        
        for step_name, step_func in setup_steps:
            print(f"\n{'='*20} {step_name} {'='*20}")
            try:
                if not step_func():
                    all_successful = False
                    print(f"\n⚠️ {step_name} failed - continuing with remaining steps...")
            except Exception as e:
                print(f"\n❌ {step_name} crashed with error: {e}")
                all_successful = False
        
        # Generate final report
        print("\n" + "=" * 70)
        print("📋 GENERATING SETUP REPORT")
        print("=" * 70)
        
        report = self.generate_setup_report()
        print(report)
        
        # Save report to file
        report_file = self.project_root / "setup_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\nDetailed setup report saved to: {report_file}")
        
        if all_successful:
            print("\nDEVELOPMENT ENVIRONMENT SETUP COMPLETED SUCCESSFULLY!")
            print("\nYour AI ERP SaaS application is now running and ready for development!")
            print("\nQuick Start Commands:")
            print("  make help          - Show all available commands")
            print("  make test          - Run all tests")
            print("  make logs          - View service logs")
            print("  make status        - Check service status")
            print("  make stop          - Stop all services")
            return True
        else:
            print("\nSETUP COMPLETED WITH ISSUES")
            print("Please review the setup report and resolve any failed steps.")
            return False

def main():
    setup = DevSetup()
    success = setup.setup_development_environment()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())












