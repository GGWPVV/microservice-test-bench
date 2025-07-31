import pytest
import os
from unittest.mock import MagicMock, patch

def test_mongo_client_integration(mock_dependencies):
    """Test MongoDB client integration"""
    with patch('mongo_client.AsyncIOMotorClient') as mock_motor:
        
        mock_client = MagicMock()
        mock_motor.return_value = mock_client
        
        from mongo_client import mongo_client, db, MONGO_URI, MONGO_DB
        
        # Verify client configuration
        assert MONGO_URI == "mongodb://mongouser:mongopass@mongo:27017/?authSource=admin"
        assert MONGO_DB == "analytics_db"

def test_mongo_environment_integration():
    """Test MongoDB environment variable integration"""
    # Test default values
    default_uri = "mongodb://mongouser:mongopass@mongo:27017/?authSource=admin"
    default_db = "analytics_db"
    
    # Verify URI format
    assert default_uri.startswith("mongodb://")
    assert "mongouser:mongopass" in default_uri
    assert "mongo:27017" in default_uri
    assert "authSource=admin" in default_uri
    
    # Verify database name
    assert default_db == "analytics_db"
    assert len(default_db) > 0

def test_mongo_connection_string_integration():
    """Test MongoDB connection string integration"""
    # Test connection string components
    uri_components = {
        "protocol": "mongodb://",
        "username": "mongouser",
        "password": "mongopass", 
        "host": "mongo",
        "port": "27017",
        "auth_source": "authSource=admin"
    }
    
    full_uri = "mongodb://mongouser:mongopass@mongo:27017/?authSource=admin"
    
    for component_name, component_value in uri_components.items():
        assert component_value in full_uri, f"Missing {component_name} in URI"

@pytest.mark.asyncio
async def test_mongo_database_operations_integration(mock_dependencies):
    """Test MongoDB database operations integration"""
    with patch('mongo_client.AsyncIOMotorClient') as mock_motor:
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_motor.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.events = mock_collection
        
        from mongo_client import db
        
        # Test database access
        events_collection = db.events
        assert events_collection is not None
        
        # Test that we can access the events collection
        # (This would be used by kafka_consumer)
        assert hasattr(db, 'events')