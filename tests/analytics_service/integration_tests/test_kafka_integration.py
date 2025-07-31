import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock

@pytest.mark.asyncio
async def test_kafka_consumer_integration(mock_dependencies):
    """Test Kafka consumer integration with MongoDB"""
    with patch('kafka_consumer.AIOKafkaConsumer') as mock_consumer_class, \
         patch('kafka_consumer.db') as mock_db:
        
        from kafka_consumer import consume
        
        # Setup mocks
        mock_consumer = MagicMock()
        mock_consumer.start = AsyncMock()
        mock_consumer.stop = AsyncMock()
        mock_consumer_class.return_value = mock_consumer
        
        # Mock message
        mock_message = MagicMock()
        mock_message.topic = "user.registered"
        mock_message.value.decode.return_value = '{"user_id": "123", "username": "testuser"}'
        
        # Mock async iterator that yields one message then stops
        async def mock_messages():
            yield mock_message
            # Simulate stopping after one message
            mock_consumer.stop.side_effect = lambda: None
            return
        
        mock_consumer.__aiter__ = lambda self: mock_messages()
        mock_db.events.insert_one = AsyncMock()
        
        # Test with timeout to prevent infinite loop
        try:
            await asyncio.wait_for(consume(), timeout=1.0)
        except asyncio.TimeoutError:
            pass  # Expected for infinite consumer loop
        
        # Verify consumer was started
        mock_consumer.start.assert_called_once()
        # Verify message was processed and stored
        mock_db.events.insert_one.assert_called_once_with({"user_id": "123", "username": "testuser"})

@pytest.mark.asyncio
async def test_kafka_consumer_json_error_handling(mock_dependencies):
    """Test Kafka consumer handles JSON decode errors"""
    with patch('kafka_consumer.AIOKafkaConsumer') as mock_consumer_class, \
         patch('kafka_consumer.db') as mock_db:
        
        from kafka_consumer import consume
        
        mock_consumer = MagicMock()
        mock_consumer.start = AsyncMock()
        mock_consumer.stop = AsyncMock()
        mock_consumer_class.return_value = mock_consumer
        
        # Mock message with invalid JSON
        mock_message = MagicMock()
        mock_message.topic = "user.registered"
        mock_message.value.decode.return_value = 'invalid json'
        
        async def mock_messages():
            yield mock_message
            return
        
        mock_consumer.__aiter__ = lambda self: mock_messages()
        mock_db.events.insert_one = AsyncMock()
        
        try:
            await asyncio.wait_for(consume(), timeout=1.0)
        except asyncio.TimeoutError:
            pass
        
        # Verify consumer started but no data was inserted due to JSON error
        mock_consumer.start.assert_called_once()
        mock_db.events.insert_one.assert_not_called()

def test_kafka_topics_integration():
    """Test Kafka topics configuration integration"""
    from kafka_consumer import KAFKA_TOPICS
    
    expected_topics = [
        "user.registered",
        "user.logged_in", 
        "score.rolled",
        "discount.calculated"
    ]
    
    # Test that topics are properly configured
    assert len(KAFKA_TOPICS) == 4
    for topic in expected_topics:
        assert topic in KAFKA_TOPICS
    
    # Test topic naming convention
    for topic in KAFKA_TOPICS:
        assert "." in topic  # All topics use dot notation
        assert len(topic.split(".")) == 2  # service.action format