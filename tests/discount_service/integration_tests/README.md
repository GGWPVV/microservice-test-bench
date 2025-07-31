# Discount Service Integration Tests

## Overview
Integration tests for Discount Service FastAPI endpoints using TestClient. These tests cover full HTTP request/response cycles with mocked dependencies.

## Test Structure
- `test_endpoints.py` - All FastAPI endpoint integration tests
- `conftest.py` - Shared pytest fixtures for dependency mocking
- `requirements.txt` - Test dependencies
- `pytest.ini` - Pytest configuration

## Running Tests

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

## Test Coverage
- **POST /discount** - All discount calculation scenarios
  - Age-based discount (40+)
  - Leaderboard-based discount (top players)
  - Combined discounts
  - No discount scenarios
  - Cached results
  - Invalid tokens
  - Invalid user data
- **GET /health** - Health check endpoint

## Key Features
- Uses FastAPI TestClient for real HTTP testing
- Mocks external dependencies (Redis, JWT, external services)
- Tests complete request/response cycles
- Validates HTTP status codes and response data
- Covers all discount calculation logic
- Tests caching behavior

## Test Philosophy
- **Integration Level**: Tests HTTP endpoints end-to-end
- **Isolated Dependencies**: External services are mocked
- **Real FastAPI**: Uses actual FastAPI application instance
- **Business Logic**: Validates discount calculation rules