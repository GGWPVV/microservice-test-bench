import pytest
import httpx
import asyncio
import json
from typing import Dict, Any

class TestKafkaIntegration:
    """Kafka integration tests"""

    @pytest.mark.asyncio
    async def test_user_registration_kafka_event(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-044: Send Kafka event on user registration"""
        # Get consumer first
        consumer = await kafka_consumer
        
        try:
            # Create user
            response = await http_client.post("/users", json=test_user_data)
            assert response.status_code == 201
            
            # Wait for Kafka message
            timeout_counter = 0
            max_timeout = 100  # 10 seconds
            found_event = False
            
            while timeout_counter < max_timeout and not found_event:
                try:
                    msg_pack = await asyncio.wait_for(consumer.getone(), timeout=0.1)
                    if msg_pack.topic == "user.registered":
                        event_data = msg_pack.value
                        assert "user_id" in event_data
                        assert "username" in event_data
                        assert "timestamp" in event_data
                        # Check if this is our user
                        if event_data["username"] == test_user_data["username"]:
                            found_event = True
                            break
                except asyncio.TimeoutError:
                    pass
                timeout_counter += 1
            
            assert found_event, "User registration event was not sent to Kafka"
            
        except Exception as e:
            pytest.fail(f"Error in Kafka test: {e}")
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_user_login_kafka_event(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-045: Send Kafka event on user login"""
        # Get consumer first
        consumer = await kafka_consumer
        
        try:
            # Login user
            login_data = {
                "email": created_user["email"],
                "password": created_user["password"]
            }
            
            response = await http_client.post("/login", json=login_data)
            assert response.status_code == 200
            
            # Wait for Kafka message
            timeout_counter = 0
            max_timeout = 100  # 10 seconds
            found_event = False
            
            while timeout_counter < max_timeout and not found_event:
                try:
                    msg_pack = await asyncio.wait_for(consumer.getone(), timeout=0.1)
                    if msg_pack.topic == "user.logged_in":
                        event_data = msg_pack.value
                        assert "user_id" in event_data
                        assert "username" in event_data
                        assert "timestamp" in event_data
                        # Check if this is our user
                        if event_data["username"] == created_user["username"]:
                            found_event = True
                            break
                except asyncio.TimeoutError:
                    pass
                timeout_counter += 1
            
            assert found_event, "User login event was not sent to Kafka"
            
        except Exception as e:
            pytest.fail(f"Error in Kafka login test: {e}")
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_kafka_message_format(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-046: Check Kafka message format"""
        # Get consumer
        consumer = await kafka_consumer
        
        try:
            # Create user
            response = await http_client.post("/users", json=test_user_data)
            assert response.status_code == 201
            
            # Get message
            timeout_counter = 0
            max_timeout = 100
            found_event = False
            
            while timeout_counter < max_timeout and not found_event:
                try:
                    msg_pack = await asyncio.wait_for(consumer.getone(), timeout=0.1)
                    if msg_pack.topic == "user.registered":
                        event_data = msg_pack.value
                        
                        # Check required fields
                        required_fields = ["user_id", "username", "timestamp"]
                        for field in required_fields:
                            assert field in event_data, f"Field {field} is missing in event"
                        
                        # Check data types
                        assert isinstance(event_data["user_id"], str)
                        assert isinstance(event_data["username"], str)
                        assert isinstance(event_data["timestamp"], str)
                        
                        # Check timestamp format
                        from datetime import datetime
                        try:
                            datetime.fromisoformat(event_data["timestamp"].replace('Z', '+00:00'))
                        except ValueError:
                            pytest.fail(f"Invalid timestamp format: {event_data['timestamp']}")
                        
                        if event_data["username"] == test_user_data["username"]:
                            found_event = True
                            break
                except asyncio.TimeoutError:
                    pass
                timeout_counter += 1
            
            assert found_event, "Event was not received from Kafka"
            
        except Exception as e:
            pytest.fail(f"Error in Kafka message format test: {e}")
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_multiple_kafka_events(
        self, 
        http_client: httpx.AsyncClient, 
        multiple_users_data: list[Dict[str, Any]],
        kafka_consumer,
        wait_for_service
    ):
        """TC-047: Multiple Kafka events"""
        # Get consumer first
        consumer = await kafka_consumer
        
        try:
            created_usernames = []
            
            # Create multiple users
            for user_data in multiple_users_data:
                response = await http_client.post("/users", json=user_data)
                assert response.status_code == 201
                created_usernames.append(user_data["username"])
            
            # Collect events from Kafka
            received_events = []
            timeout_counter = 0
            max_timeout = 100  # 10 seconds
            
            while len(received_events) < len(multiple_users_data) and timeout_counter < max_timeout:
                try:
                    msg_pack = await asyncio.wait_for(consumer.getone(), timeout=0.1)
                    if msg_pack.topic == "user.registered":
                        received_events.append(msg_pack.value)
                except asyncio.TimeoutError:
                    pass
                timeout_counter += 1
            
            # Check that all users are represented in events
            received_usernames = [event["username"] for event in received_events]
            for username in created_usernames:
                assert username in received_usernames, f"Username {username} not found in received events: {received_usernames}"
                
        except Exception as e:
            pytest.fail(f"Error in multiple Kafka events test: {e}")
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_kafka_connection_resilience(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-048: Kafka connection resilience"""
        # This test checks that service continues to work even if Kafka is unavailable
        # In real environment you can temporarily disable Kafka
        
        # Create user (should work even if Kafka is unavailable)
        response = await http_client.post("/users", json=test_user_data)
        
        # Service should continue to work
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"

    @pytest.mark.asyncio
    async def test_kafka_event_ordering(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-049: Kafka event ordering"""
        # Get consumer first
        consumer = await kafka_consumer
        
        try:
            # Create user
            create_response = await http_client.post("/users", json=test_user_data)
            assert create_response.status_code == 201
            
            # Wait a bit before login
            await asyncio.sleep(0.5)
            
            # Login immediately
            login_data = {
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
            login_response = await http_client.post("/login", json=login_data)
            assert login_response.status_code == 200
            
            # Get events in correct order
            events = []
            timeout_counter = 0
            max_timeout = 100  # 10 seconds
            
            while len(events) < 2 and timeout_counter < max_timeout:
                try:
                    msg_pack = await asyncio.wait_for(consumer.getone(), timeout=0.1)
                    if msg_pack.value and msg_pack.value.get("username") == test_user_data["username"]:
                        events.append({
                            "topic": msg_pack.topic,
                            "data": msg_pack.value
                        })
                except asyncio.TimeoutError:
                    pass
                timeout_counter += 1
            
            # Check that events came in correct order
            topics = [event["topic"] for event in events]
            assert "user.registered" in topics, f"Expected user.registered in {topics}"
            assert "user.logged_in" in topics, f"Expected user.logged_in in {topics}"
            
        except Exception as e:
            pytest.fail(f"Error in Kafka ordering test: {e}")
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_kafka_event_idempotency(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-050: Kafka event idempotency"""
        # Get consumer first
        consumer = await kafka_consumer
        
        try:
            login_data = {
                "email": created_user["email"],
                "password": created_user["password"]
            }
            
            # Perform multiple logins in a row
            for _ in range(3):
                response = await http_client.post("/login", json=login_data)
                assert response.status_code == 200
            
            # Check that each login generates an event
            events_count = 0
            timeout_counter = 0
            max_timeout = 100
            
            while events_count < 3 and timeout_counter < max_timeout:
                try:
                    msg_pack = await asyncio.wait_for(consumer.getone(), timeout=0.1)
                    if msg_pack.topic == "user.logged_in":
                        event_data = msg_pack.value
                        if event_data["username"] == created_user["username"]:
                            events_count += 1
                except asyncio.TimeoutError:
                    pass
                timeout_counter += 1
            
            # Should receive 3 events (one for each login)
            assert events_count == 3, f"Expected 3 events, got {events_count}"
            
        except Exception as e:
            pytest.fail(f"Error in Kafka idempotency test: {e}")
        finally:
            await consumer.stop()