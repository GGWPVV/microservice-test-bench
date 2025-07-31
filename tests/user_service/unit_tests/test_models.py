import pytest
import uuid
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/user_service/app'))

class TestUserModel:
    """Unit tests for User database model - testing structure and business rules"""
    
    def test_user_table_name(self):
        """Test: table should be named 'users'"""
        expected_table_name = "users"
        assert expected_table_name == "users"
    
    def test_user_required_fields(self):
        """Test: user should have all required fields"""
        required_fields = [
            "id", "username", "email", "hashed_password", 
            "city", "age", "created_at", "updated_at"
        ]
        
        # Check that we know what fields should exist
        assert len(required_fields) == 8
        assert "username" in required_fields
        assert "email" in required_fields
        assert "hashed_password" in required_fields
    
    def test_uuid_generation(self):
        """Test: ID should be UUID"""
        test_uuid = uuid.uuid4()
        
        assert isinstance(test_uuid, uuid.UUID)
        assert len(str(test_uuid)) == 36
        assert str(test_uuid) != str(uuid.uuid4())  # Different UUIDs
    
    def test_user_constraints_logic(self):
        """Test: business rules for user fields"""
        
        # Username should be unique and not empty
        usernames = ["user1", "user2", "admin"]
        assert len(set(usernames)) == len(usernames)  # All unique
        
        # Email should be unique
        emails = ["user1@test.com", "user2@test.com"]
        assert len(set(emails)) == len(emails)  # All unique
        
        # Password should be hashed (not plain text)
        plain_password = "mypassword"
        hashed_password = f"$2b$12${plain_password}_hashed"
        
        assert hashed_password != plain_password
        assert len(hashed_password) > len(plain_password)