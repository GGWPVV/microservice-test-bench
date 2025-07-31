# Score Service Integration Tests

## Overview
Integration tests for Score Service FastAPI endpoints using TestClient. These tests cover full HTTP request/response cycles with mocked dependencies.

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
- **POST /roll** - Score generation, duplicate prevention, token validation
- **GET /leaderboard** - Cache hit/miss scenarios, data retrieval
- **DELETE /leaderboard/cache** - Cache clearing functionality
- **GET /health** - Health check endpoint

## Key Features
- Uses FastAPI TestClient for real HTTP testing
- Mocks external dependencies (Redis, Database, Kafka)
- Tests complete request/response cycles
- Validates HTTP status codes and response data
- Covers error scenarios and edge cases

## Test Philosophy
- **Integration Level**: Tests HTTP endpoints end-to-end
- **Isolated Dependencies**: External services are mocked
- **Real FastAPI**: Uses actual FastAPI application instance
- **HTTP Focus**: Validates request/response handling