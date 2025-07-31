# Discount Service Unit Tests

## Overview
Unit tests for the Discount Service microservice covering discount calculation, JWT token validation, user service integration, and leaderboard checking.

## Test Structure
- `test_main.py` - FastAPI endpoints and business logic tests
- `test_schemas.py` - Pydantic schema validation tests
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
pytest test_main.py
pytest test_schemas.py
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
- **Discount Calculation**: Age-based and leaderboard-based discount logic
- **JWT Token Handling**: Token decoding, validation, and error handling
- **User Service Integration**: User info retrieval and error scenarios
- **Leaderboard Integration**: Top player checking via score service
- **Caching Logic**: Redis cache hit/miss scenarios
- **Schema Validation**: Pydantic models for all input/output schemas
- **Error Handling**: Authentication failures, invalid data, and edge cases

## Mocked Dependencies
- Kafka producer functionality
- Redis cache operations
- JWT token operations
- External service calls (user_service, score_service)
- Logger functionality

## Test Philosophy
- **Unit Tests**: Test business logic in isolation
- **Fast Execution**: No real Redis, JWT, or network calls
- **Clear Assertions**: Each test validates specific behavior
- **Edge Cases**: Include boundary conditions and error scenarios
- **Async Support**: Proper handling of async/await patterns