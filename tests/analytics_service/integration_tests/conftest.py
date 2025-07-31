import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/analytics_service/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared'))

@pytest.fixture
def mock_dependencies():
    with patch('main.setup_logger'), \
         patch('kafka_consumer.setup_logger'), \
         patch('mongo_client.setup_logger'), \
         patch('kafka_consumer.db'), \
         patch('kafka_consumer.AIOKafkaConsumer'), \
         patch('mongo_client.AsyncIOMotorClient'):
        yield