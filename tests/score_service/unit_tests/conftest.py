import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/score_service/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared'))

# Mock modules before any imports
sys.modules['kafka_client'] = MagicMock()
sys.modules['logger_config'] = MagicMock()
sys.modules['redis_client'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Mock database module with SessionLocal
mock_database = MagicMock()
mock_database.SessionLocal = MagicMock()
sys.modules['database'] = mock_database