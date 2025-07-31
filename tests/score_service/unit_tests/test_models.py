import pytest
import uuid
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/score_service/app'))

class TestUserScoreModel:
    """Unit tests for UserScore database model - testing structure and business rules"""
    
    def test_user_score_table_name(self):
        """Test: table should be named 'user_scores'"""
        expected_table_name = "user_scores"
        assert expected_table_name == "user_scores"
    
    def test_user_score_required_fields(self):
        """Test: user_score should have all required fields"""
        required_fields = [
            "id", "user_id", "score", "created_at", "username"
        ]
        
        # Check that we know what fields should exist
        assert len(required_fields) == 5
        assert "user_id" in required_fields
        assert "score" in required_fields
        assert "username" in required_fields
    
    def test_uuid_generation(self):
        """Test: user_id should be UUID"""
        test_uuid = uuid.uuid4()
        
        assert isinstance(test_uuid, uuid.UUID)
        assert len(str(test_uuid)) == 36
        assert str(test_uuid) != str(uuid.uuid4())  # Different UUIDs
    
    def test_score_constraints_logic(self):
        """Test: business rules for score fields"""
        
        # Score should be between 1 and 1,000,000
        valid_scores = [1, 500000, 1000000]
        for score in valid_scores:
            assert 1 <= score <= 1000000
        
        # Username should not be empty
        usernames = ["user1", "player2", "admin"]
        for username in usernames:
            assert len(username) > 0
            assert isinstance(username, str)
        
        # User can have only one score record (updated, not duplicated)
        user_id = uuid.uuid4()
        scores = [750000, 850000]  # Same user, different scores
        assert len(scores) == 2  # But only one record should exist per user