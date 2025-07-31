import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/discount_service/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared'))

@pytest.fixture
def mock_dependencies():
    with patch('main.setup_logger'), \
         patch('main.start_kafka_producer', new_callable=AsyncMock), \
         patch('main.stop_kafka_producer', new_callable=AsyncMock), \
         patch('main.publish_event', new_callable=AsyncMock), \
         patch('main.get_redis', new_callable=AsyncMock), \
         patch('main.RedisCache'), \
         patch('main.decode_token'), \
         patch('main.get_user_info'), \
         patch('main.is_user_in_top'):
        yield