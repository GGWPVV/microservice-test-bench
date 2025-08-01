# User Service Integration Tests

Comprehensive integration test suite for user_service in production style.

## Test Structure

### 📁 Test Files

- **`test_user_registration.py`** - User registration tests (TC-001 - TC-011)
- **`test_authentication.py`** - Authentication and JWT token tests (TC-012 - TC-023)
- **`test_user_management.py`** - User management tests (TC-024 - TC-031)
- **`test_health_and_monitoring.py`** - Service health tests (TC-032 - TC-043)
- **`test_kafka_integration.py`** - Kafka integration tests (TC-044 - TC-050)
- **`test_database_integration.py`** - Database integration tests (TC-051 - TC-060)
- **`test_security.py`** - Security tests (TC-061 - TC-071)
- **`test_performance.py`** - Performance tests (TC-072 - TC-082)

### 🔧 Configuration

- **`conftest.py`** - Test fixtures and settings
- **`pytest.ini`** - Pytest configuration
- **`requirements.txt`** - Test dependencies
- **`run_tests.py`** - Test runner script
- **`run_coverage.py`** - Coverage analysis script
- **`.coveragerc`** - Coverage configuration

## Test Coverage

### ✅ Functional Areas

1. **User Registration**
   - Successful registration
   - Field validation (email, password, age)
   - Username/email uniqueness checks
   - Boundary values

2. **Authentication**
   - Successful login
   - Invalid credentials
   - JWT tokens (structure, expiration)
   - Protected endpoints

3. **User Management**
   - Get users list
   - Get current user
   - Data consistency

4. **Integrations**
   - Kafka events (registration, login)
   - Database (persistence, constraints)
   - Health checks

5. **Security**
   - SQL injection protection
   - XSS protection
   - Input validation
   - Token security

6. **Performance**
   - Endpoint response times
   - Concurrent requests
   - Load testing

## Running Tests

### 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run tests with coverage analysis
python run_coverage.py

# Or directly via pytest
python -m pytest -v
```

### 📈 Coverage Analysis

```bash
# Run tests with coverage
python run_coverage.py

# Or manually with pytest-cov
python -m pytest --cov=../../../projects/user_service/app --cov-report=html --cov-report=term-missing

# View HTML coverage report
# Open htmlcov/index.html in browser
```

### 🎯 Selective Test Execution

```bash
# Registration tests only
python -m pytest test_user_registration.py -v

# Security tests only
python -m pytest test_security.py -v

# Fast tests only (exclude performance)
python -m pytest -m "not performance" -v

# Specific test
python -m pytest test_user_registration.py::TestUserRegistration::test_successful_user_registration -v
```

### 🔧 Environment Variables

```bash
# Service URL (default: http://localhost:8000)
export USER_SERVICE_URL=http://localhost:8000

# Kafka servers (default: localhost:9092)
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

## Prerequisites

### 🐳 Docker Compose

Ensure all required services are running:

```bash
docker-compose up -d user_service userdb kafka redis
```

### 📋 Readiness Check

The `run_tests.py` script automatically checks service readiness before running tests.

## Test Results

### 📊 Reports

Tests generate detailed reports with:
- Status of each test
- Execution time
- Detailed error logs

### 🏷️ Test Markers

- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.kafka` - Kafka tests
- `@pytest.mark.database` - Database tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.performance` - Performance tests

## Test Architecture

### 🏗️ Principles

1. **Isolation** - Each test is independent
2. **Idempotency** - Tests can be run multiple times
3. **Realism** - Tests are as close to production conditions as possible
4. **Completeness** - Coverage of all critical scenarios

### 🔄 Lifecycle

1. **Setup** - Test data preparation
2. **Execution** - Test scenario execution
3. **Verification** - Result verification
4. **Cleanup** - Automatic cleanup via fixtures

## Troubleshooting

### ❗ Common Issues

1. **Service not ready**
   - Check `docker-compose ps`
   - Increase timeout in `conftest.py`

2. **Kafka unavailable**
   - Check `KAFKA_BOOTSTRAP_SERVERS`
   - Ensure Kafka is running

3. **Port conflicts**
   - Check that ports 8000, 9092, 5432 are free

4. **Tests fail randomly**
   - Increase timeouts in tests
   - Check system resources

### 🔍 Debugging

```bash
# Run with maximum verbosity
python -m pytest -v -s --tb=long

# Run specific test with debugging
python -m pytest test_file.py::test_name -v -s --pdb
```

## Quality Metrics

### 📈 Target Metrics

- **Code Coverage**: > 90%
- **Execution Time**: < 5 minutes for all tests
- **Stability**: > 99% successful runs
- **Performance**: All endpoints < 2 sec

### 🎯 Test KPIs

- 82 test cases (TC-001 - TC-082)
- 8 functional areas
- Complete API endpoint coverage
- All integrations verified