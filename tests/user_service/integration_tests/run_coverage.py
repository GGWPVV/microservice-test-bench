#!/usr/bin/env python3
"""
Script for running integration tests with coverage analysis
"""

import subprocess
import sys
import os
import time
import requests
from typing import List, Optional

def check_service_health(url: str, max_attempts: int = 30, delay: int = 2) -> bool:
    """Checks service readiness"""
    print(f"Checking service readiness: {url}")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Service ready (attempt {attempt + 1})")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for service readiness (attempt {attempt + 1}/{max_attempts})")
        time.sleep(delay)
    
    print(f"❌ Service not ready after {max_attempts} attempts")
    return False

def run_coverage_tests() -> int:
    """Runs tests with coverage analysis"""
    # Get service source path
    service_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "..", "..", "projects", "user_service", "app"
    )
    service_path = os.path.abspath(service_path)
    
    if not os.path.exists(service_path):
        print(f"❌ Service source path not found: {service_path}")
        return 1
    
    print(f"📁 Service source path: {service_path}")
    
    # Coverage command
    cmd = [
        "python", "-m", "pytest",
        ".",
        "--cov=" + service_path,
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-report=xml:coverage.xml",
        "--cov-fail-under=70",  # Minimum 70% coverage
        "-v",
        "--tb=short"
    ]
    
    print(f"🧪 Running tests with coverage...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    
    if result.returncode == 0:
        print("✅ Tests passed with sufficient coverage!")
        print("📊 Coverage reports generated:")
        print("  - HTML: htmlcov/index.html")
        print("  - XML: coverage.xml")
    else:
        print(f"❌ Tests failed or coverage insufficient (code: {result.returncode})")
    
    return result.returncode

def main():
    """Main function"""
    service_url = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
    
    print("🚀 Running user_service integration tests with coverage")
    print(f"Service URL: {service_url}")
    print("-" * 60)
    
    # Check service readiness
    if not check_service_health(service_url):
        print("❌ Service not ready. Terminating tests.")
        return 1
    
    # Run tests with coverage
    exit_code = run_coverage_tests()
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())