import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/analytics_service/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared'))

# Mock modules before any imports
sys.modules['kafka_consumer'] = MagicMock()
sys.modules['logger_config'] = MagicMock()
sys.modules['mongo_client'] = MagicMock()
sys.modules['aiokafka'] = MagicMock()
sys.modules['motor.motor_asyncio'] = MagicMock()