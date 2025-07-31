# Score Service Unit Tests

## Overview
Unit tests for the Score Service microservice covering score generation, leaderboards, caching, and user client integration.

## Test Structure
- `test_main.py` - FastAPI endpoints and business logic tests
- `test_models.py` - Database UserScore model structure tests  
- `test_schemas.py` - Pydantic schema validation tests
- `test_user_client.py` - User service client integration tests
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
pytest test_models.py
pytest test_schemas.py
pytest test_user_client.py
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
- **Score Rolling**: Score generation, duplicate roll prevention, user validation
- **Leaderboard**: Top 10 retrieval, caching logic, cache invalidation
- **Database Models**: UserScore model structure and business rules
- **API Schemas**: Pydantic validation for all input/output schemas
- **User Client**: External user service integration and error handling
- **Error Handling**: Validation errors, authentication failures, and edge cases

## Mocked Dependencies
- Kafka producer/consumer functionality
- Redis cache operations
- Database connections and SQLAlchemy models
- Logger functionality
- External user service calls
- Random score generation (for deterministic testing)

## Test Philosophy
- **Unit Tests**: Test business logic in isolation
- **Fast Execution**: No real database, Redis, or network calls
- **Clear Assertions**: Each test validates specific behavior
- **Edge Cases**: Include boundary conditions and error scenarios
- **Async Support**: Proper handling of async/await patterns