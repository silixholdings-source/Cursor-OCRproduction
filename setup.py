#!/usr/bin/env python3
"""
Setup script for AI ERP SaaS application
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {command}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return None

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Docker
    if not shutil.which("docker"):
        print("❌ Docker is not installed. Please install Docker first.")
        return False
    
    # Check Docker Compose
    if not shutil.which("docker-compose"):
        print("❌ Docker Compose is not installed. Please install Docker Compose first.")
        return False
    
    # Check Node.js
    if not shutil.which("node"):
        print("❌ Node.js is not installed. Please install Node.js first.")
        return False
    
    # Check Python
    if not shutil.which("python"):
        print("❌ Python is not installed. Please install Python first.")
        return False
    
    print("✅ All prerequisites are installed!")
    return True

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from env.example")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No env.example file found, you may need to create .env manually")

def install_dependencies():
    """Install all dependencies"""
    print("📦 Installing dependencies...")
    
    # Install root dependencies
    run_command("npm install")
    
    # Install backend dependencies
    print("Installing Python backend dependencies...")
    run_command("pip install -r requirements.txt", cwd="backend")
    
    # Install web dependencies
    print("Installing web frontend dependencies...")
    run_command("npm install", cwd="web")
    
    # Install mobile dependencies
    print("Installing mobile app dependencies...")
    run_command("npm install", cwd="mobile")

def build_containers():
    """Build Docker containers"""
    print("🐳 Building Docker containers...")
    
    run_command("docker-compose -f docker-compose.dev.yml build")

def start_development():
    """Start development environment"""
    print("🚀 Starting development environment...")
    
    run_command("docker-compose -f docker-compose.dev.yml up -d postgres redis")
    print("⏳ Waiting for databases to be ready...")
    
    # Wait a bit for databases to start
    import time
    time.sleep(10)
    
    print("🏃 Starting application services...")
    run_command("docker-compose -f docker-compose.dev.yml up -d")

def show_status():
    """Show application status"""
    print("\n🎉 Setup complete!")
    print("\n📍 Application URLs:")
    print("  - Backend API: http://localhost:8000")
    print("  - API Documentation: http://localhost:8000/docs")
    print("  - Web Frontend: http://localhost:3000")
    print("  - PostgreSQL: localhost:5432")
    print("  - Redis: localhost:6379")
    
    print("\n🛠️  Useful commands:")
    print("  - View logs: docker-compose -f docker-compose.dev.yml logs -f")
    print("  - Stop services: docker-compose -f docker-compose.dev.yml down")
    print("  - Restart services: docker-compose -f docker-compose.dev.yml restart")
    print("  - Run tests: docker-compose -f docker-compose.dev.yml exec backend pytest")

def main():
    """Main setup function"""
    print("🚀 AI ERP SaaS Setup Script")
    print("=" * 50)
    
    if not check_prerequisites():
        sys.exit(1)
    
    setup_environment()
    install_dependencies()
    build_containers()
    start_development()
    show_status()

if __name__ == "__main__":
    main()
