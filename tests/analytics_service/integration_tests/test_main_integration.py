import pytest
import asyncio
import socket
from unittest.mock import MagicMock, patch, AsyncMock

@pytest.mark.asyncio
async def test_wait_for_kafka_integration(mock_dependencies):
    """Test Kafka connection waiting integration"""
    with patch('socket.create_connection') as mock_connection:
        from main import wait_for_kafka
        
        # Mock successful connection
        mock_connection.return_value.__enter__ = MagicMock()
        mock_connection.return_value.__exit__ = MagicMock()
        
        # Test successful connection
        await wait_for_kafka("kafka", 9092, timeout=1)
        
        mock_connection.assert_called_once_with(("kafka", 9092), timeout=2)

@pytest.mark.asyncio
async def test_wait_for_kafka_retry_integration(mock_dependencies):
    """Test Kafka connection retry logic integration"""
    with patch('socket.create_connection') as mock_connection, \
         patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep, \
         patch('asyncio.get_event_loop') as mock_loop:
        
        from main import wait_for_kafka
        
        # Mock time progression
        mock_loop.return_value.time.side_effect = [0, 1, 2]
        # First call fails, second succeeds
        mock_connection.side_effect = [OSError(), MagicMock()]
        
        await wait_for_kafka("kafka", 9092, timeout=10)
        
        # Verify retry logic
        assert mock_connection.call_count == 2
        mock_sleep.assert_called_once_with(2)

@pytest.mark.asyncio
async def test_wait_for_kafka_timeout_integration(mock_dependencies):
    """Test Kafka connection timeout integration"""
    with patch('socket.create_connection') as mock_connection, \
         patch('asyncio.get_event_loop') as mock_loop:
        
        from main import wait_for_kafka
        
        # Mock timeout scenario
        mock_loop.return_value.time.side_effect = [0, 70]  # Exceeds timeout
        mock_connection.side_effect = OSError()
        
        with pytest.raises(TimeoutError):
            await wait_for_kafka("kafka", 9092, timeout=60)

@pytest.mark.asyncio
async def test_main_integration(mock_dependencies):
    """Test main function integration"""
    with patch('main.wait_for_kafka', new_callable=AsyncMock) as mock_wait, \
         patch('main.consume', new_callable=AsyncMock) as mock_consume:
        
        from main import main
        
        await main()
        
        # Verify main flow
        mock_wait.assert_called_once_with("kafka", 9092, timeout=60)
        mock_consume.assert_called_once()

def test_service_configuration_integration():
    """Test service configuration integration"""
    # Test that service can be imported and configured
    try:
        from main import wait_for_kafka, main
        from kafka_consumer import consume, KAFKA_TOPICS
        
        # Verify functions are callable
        assert callable(wait_for_kafka)
        assert callable(main)
        assert callable(consume)
        
        # Verify configuration
        assert isinstance(KAFKA_TOPICS, list)
        assert len(KAFKA_TOPICS) > 0
        
    except ImportError as e:
        pytest.fail(f"Service configuration failed: {e}")