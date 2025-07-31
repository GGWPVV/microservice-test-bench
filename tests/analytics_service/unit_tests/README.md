# Analytics Service Unit Tests

## Overview
Unit tests for the Analytics Service microservice covering Kafka message consumption, MongoDB storage, and event processing.

## Test Structure
- `test_main.py` - Main service logic and Kafka connection tests
- `test_kafka_consumer.py` - Kafka message consumption and processing tests
- `test_schemas.py` - Pydantic schema validation tests
- `test_mongo_client.py` - MongoDB client configuration tests
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
pytest test_kafka_consumer.py
pytest test_schemas.py
pytest test_mongo_client.py
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
- **Kafka Connection**: Connection waiting, retry logic, timeout handling
- **Message Processing**: Event consumption, JSON parsing, error handling
- **MongoDB Integration**: Client initialization, data insertion
- **Schema Validation**: Pydantic models for health and error responses
- **Configuration**: Environment variable handling

## Mocked Dependencies
- Kafka consumer and producer functionality
- MongoDB client and database operations
- Logger functionality
- Socket connections for Kafka health checks

## Test Philosophy
- **Unit Tests**: Test business logic in isolation
- **Fast Execution**: No real Kafka or MongoDB connections
- **Clear Assertions**: Each test validates specific behavior
- **Async Support**: Proper handling of async/await patterns
- **Error Scenarios**: Include network failures and data corruption cases