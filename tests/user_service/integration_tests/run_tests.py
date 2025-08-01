#!/usr/bin/env python3
"""
Скрипт для запуска интеграционных тестов user_service
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

def run_pytest(args: List[str]) -> int:
    """Runs pytest with specified arguments"""
    cmd = ["python", "-m", "pytest"] + args
    print(f"Executing command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    return result.returncode

def main():
    """Main function"""
    # Check environment variables
    service_url = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    print("🚀 Running user_service integration tests")
    print(f"Service URL: {service_url}")
    print(f"Kafka servers: {kafka_servers}")
    print("-" * 50)
    
    # Check service readiness
    if not check_service_health(service_url):
        print("❌ Service not ready. Terminating tests.")
        return 1
    
    # Define pytest arguments
    pytest_args = [
        ".",  # Current directory
        "-v",  # Verbose output
        "--tb=short",  # Short traceback
        "--strict-markers",  # Strict markers
    ]
    
    # Add command line arguments
    if len(sys.argv) > 1:
        pytest_args.extend(sys.argv[1:])
    
    # Run tests
    print("🧪 Running tests...")
    exit_code = run_pytest(pytest_args)
    
    if exit_code == 0:
        print("✅ All tests passed successfully!")
    else:
        print(f"❌ Tests finished with code: {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())