import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import socket
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/analytics_service/app'))

with patch('main.setup_logger'), \
     patch('main.consume', new_callable=AsyncMock):
    from main import wait_for_kafka, main

class TestWaitForKafka:
    @patch('socket.create_connection')
    @patch('asyncio.get_event_loop')
    async def test_wait_for_kafka_success(self, mock_loop, mock_connection):
        """Test successful Kafka connection"""
        mock_loop.return_value.time.return_value = 0
        mock_connection.return_value.__enter__ = MagicMock()
        mock_connection.return_value.__exit__ = MagicMock()
        
        await wait_for_kafka("kafka", 9092, timeout=60)
        
        mock_connection.assert_called_once_with(("kafka", 9092), timeout=2)

    @patch('socket.create_connection')
    @patch('asyncio.get_event_loop')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_wait_for_kafka_retry_then_success(self, mock_sleep, mock_loop, mock_connection):
        """Test Kafka connection with retry"""
        mock_loop.return_value.time.side_effect = [0, 1, 2]  # Time progression
        mock_connection.side_effect = [OSError(), MagicMock()]
        
        await wait_for_kafka("kafka", 9092, timeout=60)
        
        assert mock_connection.call_count == 2
        mock_sleep.assert_called_once_with(2)

    @patch('socket.create_connection')
    @patch('asyncio.get_event_loop')
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_wait_for_kafka_timeout(self, mock_sleep, mock_loop, mock_connection):
        """Test Kafka connection timeout"""
        mock_loop.return_value.time.side_effect = [0, 70]  # Timeout after 70s
        mock_connection.side_effect = OSError()
        
        with pytest.raises(TimeoutError):
            await wait_for_kafka("kafka", 9092, timeout=60)

class TestMain:
    @patch('main.consume', new_callable=AsyncMock)
    @patch('main.wait_for_kafka', new_callable=AsyncMock)
    async def test_main_success(self, mock_wait_kafka, mock_consume):
        """Test successful main execution"""
        await main()
        
        mock_wait_kafka.assert_called_once_with("kafka", 9092, timeout=60)
        mock_consume.assert_called_once()