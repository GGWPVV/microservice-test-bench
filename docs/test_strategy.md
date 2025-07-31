# 🧪 Test Strategy – Microservice Discount System

_Last updated: 2025-07-31_  
_Author: Georgii Vladimirov_

---

## 1. Objective

Define a comprehensive QA approach to verify the reliability, correctness, and stability of a microservice-based backend system for scoring, discounting, and analytics.

The project is API-only and consists of multiple containerized microservices interacting via REST and Kafka.

---

## 2. Scope of Testing

### 2.1 Included

- **Functional testing** of each microservice:
  - `user_service` – registration, login, JWT issuance
  - `score_service` – score generation, leaderboard
  - `discount_service` – discount logic based on age and score
  - `analytics_service` – Kafka consumption and MongoDB logging

- **Integration testing**:
  - Kafka event flow across services
  - Redis caching behavior
  - REST communication between services

- **Exploratory testing**:
  - Ad-hoc and edge-case testing of API behavior and security validation

- **Infrastructure testing**:
  - Logging and Filebeat → Elasticsearch → Kibana pipeline
  - Kafka message delivery
  - Redis TTL behavior and expiration

### 2.2 Out of Scope

- UI testing (no frontend present)
- Load testing and performance benchmarking (optional in future)
- Security testing beyond JWT token validation

---

## 3. Test Types and Techniques

| Type                | Description                                              |
|---------------------|----------------------------------------------------------|
| Unit Tests          | Pytest-based unit checks (where implemented)             |
| API Testing         | Postman-based tests for all exposed endpoints            |
| Integration Tests   | Multi-service validation through real data flow          |
| Exploratory Testing | Manual ad-hoc scenarios to provoke edge case behavior    |
| Smoke Tests         | Basic system availability and core function validation   |
| Regression Tests    | Re-run of key tests after service changes                |
| Logging Verification| Kafka + ELK log completeness and structure               |

---

## 4. Tools and Stack

- **Test Execution**: Postman (collections), PyTest
- **Automation (partial)**: Python + PyTest
- **Message Bus**: Apache Kafka (event-driven integration)
- **Databases**: PostgreSQL, Redis, MongoDB
- **Monitoring**: Filebeat, Elasticsearch, Kibana
- **Versioning**: Git + GitHub

---

## 5. Environments

| Environment     | Description                    |
|------------------|-------------------------------|
| Local Docker     | Default dev & test environment |
| Kubernetes (WIP) | Planned full deployment        |

---

## 6. Roles & Responsibility

| Role         | Responsibility                               |
|--------------|-----------------------------------------------|
| Developer    | Implements services, handles bugfixes         |
| QA Engineer  | Writes test plans, runs Postman & integration |
| QA (Georgii) | Owns the full test architecture and execution |

---

## 7. Entry and Exit Criteria

### Entry
- All services are up and healthy (Docker/K8s)
- Required data available (e.g. Kafka up, Redis ready)
- Postman collection updated

### Exit
- All critical/happy path scenarios passed
- Integration flows verified (Kafka, Redis)
- No blocker/high bugs open

---

## 8. Risk Analysis

| Risk                                  | Mitigation                                   |
|--------------------------------------|----------------------------------------------|
| Kafka unavailable                    | Retry + local logging fallback (planned)     |
| Redis TTL conflict or cache miss     | Manual invalidation endpoint in score service|
| No frontend to validate tokens       | Use Postman and JWT.io to inspect manually   |

---

## 9. Reporting

- Logs: Structured logs (JSON) sent via Filebeat
- Metrics: Basic API response checks (time, status)
- Bug Reports: Markdown-style reports, optionally in Qase/Trello/Jira

---

## 10. References

- [requirements.md](../docs/requirements.md)
- [README.md](../README.md)
- [Kafka topics and contracts](../docs/kafka_topics.md) *(later)*

## 11. Traceability

Test cases are linked to functional requirements by unique IDs (e.g., REQ-001 ↔ TC-001).  
Traceability matrix is maintained in test plans per service.