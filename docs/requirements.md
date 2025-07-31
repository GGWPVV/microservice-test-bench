# Software Requirements Specification (SRS)
## Project: Microservice Discount System
_Version: 1.0 | Last updated: 2025-07-29 | Author: Development Team_

---

## 1. Overview

This document specifies the functional and non-functional requirements for a microservice-based discount calculation system. The system encompasses user management, score generation, discount calculation, and analytics logging across four independent microservices.

**Scope**: Core functionality with future extensibility. API-only system without user interface.

---

## 2. System Architecture

### 2.1 Architecture
The system consists of four microservices:
- **user_service**: User registration and authentication
- **score_service**: Score generation and leaderboard management  
- **discount_service**: Discount calculation based on user criteria
- **analytics_service**: Event logging and data aggregation

### 2.2 Service Communication
- **Synchronous**: REST APIs for real-time operations
- **Asynchronous**: Kafka events for decoupled communication
- **Caching**: Redis for performance optimization
- **Storage**: PostgreSQL (users, scores), MongoDB (analytics)

---

## 3. Functional Requirements

### 3.1 User Management Service (REQ-001)

#### 3.1.1 User Registration (REQ-001.1)
**Description**: System shall allow new users to register with personal information

**Input Data**:
- Username: String, 3-50 characters, alphanumeric + underscore, unique
- Email: String, valid RFC 5322 format, unique
- Password: String, minimum 6 characters (hashed with bcrypt)
- Age: Integer, range 13-120
- City: String, 1-100 characters

**Business Rules**:
- BR-001: Username must be unique across the system
- BR-002: Email must be unique across the system
- BR-003: Registration triggers `user.registered` Kafka event

**Success Response**: HTTP 201, `{"message": "User created successfully", "user_name": "john_doe"}`
**Error Responses**: 
- HTTP 422: Validation errors with field details
- HTTP 500: Internal server error

#### 3.1.2 User Authentication (REQ-001.2)
**Description**: System shall authenticate users and issue JWT tokens

**Input Data**:
- Username: String (email address)
- Password: String (plain text)

**Business Rules**:
- BR-005: JWT token expires after 2 hours
- BR-006: Token contains user ID and expiration timestamp
- BR-007: Failed attempts are logged for security monitoring
- BR-008: Successful login triggers `user.logged_in` Kafka event

**Success Response**: HTTP 200, `{"access_token": "jwt_token", "token_type": "bearer"}`
**Error Responses**:
- HTTP 401: `{"detail": "Invalid credentials"}`
- HTTP 500: Internal server error

#### 3.1.3 User Profile Access (REQ-001.3)
**Description**: System shall provide authenticated user profile information

**Input Data**: Valid JWT token in Authorization header
**Output Data**: User ID, username, age
**Business Rules**:
- BR-009: Only token owner can access their profile
- BR-010: Expired tokens are rejected

### 3.2 Score Management Service (REQ-002)

#### 3.2.1 Score Generation (REQ-002.1)
**Description**: System shall allow authenticated users to generate a random score once

**Input Data**: Valid JWT token in Authorization header
**Output Data**: Username, score value, timestamp

**Business Rules**:
- BR-011: Score range is 1 to 1,000,000 (inclusive)
- BR-012: Each user can roll exactly once (enforced via Redis)
- BR-013: Score generation triggers `score.rolled` Kafka event
- BR-014: Leaderboard cache is invalidated after new score

**Success Response**: HTTP 200, `{"username": "john", "score": 750000, "timestamp": "2025-01-01T12:00:00Z"}`
**Error Responses**:
- HTTP 400: `{"detail": "You have already rolled."}`
- HTTP 403: `{"detail": "Invalid token"}`
- HTTP 500: Internal server error

#### 3.2.2 Leaderboard Access (REQ-002.2)
**Description**: System shall provide top 10 scores ranking

**Input Data**: None (public endpoint)
**Output Data**: Array of username, score, timestamp (top 10)

**Business Rules**:
- BR-015: Results sorted by score descending
- BR-016: Results cached in Redis for 60 seconds
- BR-017: Cache automatically refreshed on expiration

### 3.3 Discount Calculation Service (REQ-003)

#### 3.3.1 Discount Calculation (REQ-003.1)
**Description**: System shall calculate user discount based on age and leaderboard position

**Input Data**: Valid JWT token in Authorization header
**Output Data**: Username, discount percentage (0.0-0.2)

**Business Rules**:
- BR-018: Age ≥ 40 years grants 10% discount
- BR-019: Top 10 leaderboard position grants 10% discount  
- BR-020: Discounts are cumulative (maximum 20%)
- BR-021: Results cached in Redis for 1 hour
- BR-022: Calculation triggers `discount.calculated` Kafka event

**Success Response**: HTTP 200, `{"username": "john", "discount": 0.2}`
**Error Responses**:
- HTTP 401: `{"detail": "Invalid token"}`
- HTTP 400: `{"detail": "Invalid user data"}`
- HTTP 500: Internal server error

### 3.4 Analytics Service (REQ-004)

#### 3.4.1 Event Processing (REQ-004.1)
**Description**: System shall consume and persist all business events

**Input Data**: Kafka messages from topics:
- `user.registered`
- `user.logged_in`
- `score.rolled`
- `discount.calculated`

**Business Rules**:
- BR-023: All events must be persisted to MongoDB
- BR-024: Event schema includes event_type, timestamp, payload
- BR-025: Failed processing attempts are retried with exponential backoff
- BR-026: Events are processed in order within each topic partition

**Success Criteria**: Events stored in MongoDB with complete data
**Error Handling**: Retry with exponential backoff, dead letter queue for failed events

### 3.5 System Health Monitoring (REQ-005)

#### 3.5.1 Health Check Endpoints (REQ-005.1)
**Description**: All services shall expose health status for monitoring

**Endpoint**: `GET /health` (public, no authentication required)
**Output Data**: `{"status": "healthy", "service": "service_name", "timestamp": "2025-01-01T12:00:00Z"}`

**Business Rules**:
- BR-027: Health check must respond within 5 seconds
- BR-028: Returns HTTP 200 when service is operational
- BR-029: Returns HTTP 500 when service has critical issues
- BR-030: Available for Kubernetes liveness/readiness probes

---

## 4. Non-Functional Requirements

### 4.1 Performance
- NFR-001: API response time < 200ms (95th percentile)
- NFR-002: System supports 100 concurrent users
- NFR-003: Leaderboard cache hit ratio > 90%
- NFR-004: Database queries optimized with proper indexing

### 4.2 Security
- NFR-005: All passwords hashed with bcrypt (cost factor 12)
- NFR-006: JWT tokens signed with HS256 algorithm
- NFR-007: No sensitive data logged in plain text
- NFR-008: Service-to-service communication over private network

### 4.3 Reliability
- NFR-009: System uptime target 99.9%
- NFR-010: Database transactions are ACID compliant
- NFR-011: Kafka message delivery guaranteed (at-least-once)
- NFR-012: Graceful degradation when Redis unavailable

### 4.4 Scalability
- NFR-013: Services are stateless and horizontally scalable
- NFR-014: Database connections pooled and managed
- NFR-015: Kafka topics partitioned for parallel processing

### 4.5 Monitoring
- NFR-016: All services expose health check endpoints
- NFR-017: Structured JSON logging for all operations
- NFR-018: Metrics collected for response times and error rates
- NFR-019: Distributed tracing for request correlation

---

## 5. System Constraints

### 5.1 Technical Constraints
- TC-001: Services deployed as Docker containers
- TC-002: PostgreSQL for relational data storage
- TC-003: MongoDB for document-based analytics storage
- TC-004: Redis for caching and session management
- TC-005: Kafka for asynchronous messaging

### 5.2 Business Constraints
- BC-001: No user interface provided (API-only system)
- BC-002: No email verification required for registration
- BC-003: No password reset functionality
- BC-004: Single score roll per user (no payment system)

### 5.3 Environmental Constraints
- EC-001: Services communicate over private network
- EC-002: External dependencies (databases, Kafka) assumed available
- EC-003: System clock synchronized across all services

---

## 6. Dependencies

### 6.1 External Dependencies
- PostgreSQL 13+ for user and score data
- MongoDB 5+ for analytics data
- Redis 6+ for caching
- Apache Kafka 2.8+ for messaging
- Elasticsearch + Kibana + Filebeat for log aggregation

### 6.2 Internal Dependencies
- discount_service depends on user_service for age data
- discount_service depends on score_service for leaderboard data
- analytics_service depends on all services for event data

---

## 7. Assumptions

- A-001: Network connectivity between services is reliable
- A-002: Database schemas are managed via migration scripts
- A-003: Kafka topics are pre-created with appropriate partitioning
- A-004: System operates in single data center (no geo-distribution)
- A-005: User load is predictable and within defined limits

---

## 8. Future Enhancements

- FE-001: OAuth2 integration for third-party authentication
- FE-002: API Gateway for centralized request routing
- FE-003: gRPC for high-performance service communication
- FE-004: Multi-roll capability with payment integration
- FE-005: Real-time leaderboard updates via WebSocket

---

**Document Control**
- **Approval Required**: Development Lead, QA Lead, Product Owner
- **Review Cycle**: Quarterly or upon major feature changes
- **Distribution**: All development team members, QA team, stakeholders