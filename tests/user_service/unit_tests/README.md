# User Service Unit Tests

## Overview
Unit tests for the User Service microservice covering authentication, user management, and core business logic.

## Test Structure
- `test_auth.py` - JWT token creation and validation tests
- `test_models.py` - Database User model structure tests  
- `test_schemas.py` - Pydantic schema validation tests
- `test_main.py` - FastAPI endpoints and business logic tests
- `conftest.py` - Shared pytest fixtures and configuration
- `requirements.txt` - Test dependencies

## Running Tests

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest test_auth.py
pytest test_models.py
pytest test_schemas.py
pytest test_main.py
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

## Test Coverage
- **Authentication**: JWT creation/validation, token expiration
- **Database Models**: User model structure and business rules
- **API Schemas**: Pydantic validation for all input/output schemas
- **API Endpoints**: User creation, login, user listing, health checks
- **Error Handling**: Validation errors and edge cases

## Mocked Dependencies
- Kafka producer/consumer functionality
- Database connections and SQLAlchemy models
- Logger functionality
- External service calls

## Test Philosophy
- **Unit Tests**: Test business logic in isolation
- **Fast Execution**: No real database or network calls
- **Clear Assertions**: Each test validates specific behavior
- **Edge Cases**: Include boundary conditions and error scenarios