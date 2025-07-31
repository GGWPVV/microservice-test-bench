# Analytics Service Integration Tests

## Overview
Integration tests for Analytics Service covering Kafka consumer integration, MongoDB operations, and service startup flow.

## Test Structure
- `test_kafka_integration.py` - Kafka consumer and message processing integration
- `test_main_integration.py` - Service startup and Kafka connection integration  
- `test_mongo_integration.py` - MongoDB client and database operations integration
- `conftest.py` - Shared pytest fixtures for dependency mocking
- `requirements.txt` - Test dependencies
- `pytest.ini` - Pytest configuration with asyncio support

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
- **Kafka Integration**: Message consumption, JSON processing, error handling
- **MongoDB Integration**: Client initialization, database operations, configuration
- **Service Startup**: Kafka connection waiting, retry logic, timeout handling
- **Main Flow**: Complete service startup and message processing flow

## Key Features
- Full async/await support with pytest-asyncio
- Mocked external dependencies (Kafka, MongoDB)
- Integration-level testing of service components
- Error handling and retry logic validation
- Configuration and environment variable testing

## Test Philosophy
- **Integration Level**: Tests component interactions
- **Async Support**: Proper handling of async service operations
- **Isolated Dependencies**: External services are mocked
- **Real Flow**: Tests actual service startup and processing flow