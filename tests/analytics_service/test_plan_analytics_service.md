# Test plan 
---


## 1.Component: Analytics service
_Version: 1.0 | Last updated: 2025-07-31 | Author: Georgii Vladimirov
---

## 2.Date of testing
from 2025-07-31 to 2025-08-02
---
## 3. Testing Environment
- **Environment**: Docker Compose setup including only the required dependencies: MongoDB, Kafka, Kafdrop, Elasticsearch, Filebeat, Kibana
- **Note**: Analytics service consumes events from other services, so user_service, score_service, discount_service should be running for integration tests
- **Config location**: See `docker-compose.yaml` in the root directory

---
## 4. Entry Testing Criteria
- All services from **Environment** are up and running
- Analytics service is built and deployed
- MongoDB is accessible and configured
- Kafka topics are created and accessible
- All dependencies are installed
- Test data is prepared
- Test cases are defined and documented
- All required environment variables are set
- Test plan is reviewed and confirmed
---

## 5. Exit Testing Criteria
- All test cases are executed
- All critical and high severity defects are resolved
- All test cases are documented with results
- Test coverage meets the defined criteria 
- No blocker or high-priority bugs remain open
---
## 6. Test Approaches, Tools, and Techniques
- **Manual Testing**: Postman, Exploratory tests via Swagger, Test cases tracked manually (or via TMS)
- **Unit Testing**: Pytest (where applicable)
- **API Testing**: Postman collection with assertions and chaining
- **Integration Testing**: Simulated multi-service calls and Kafka event validation
- **Smoke Testing**: Key endpoints health and behavior
- **Regression Testing**: Re-execution of affected test cases post changes
- **Ad-hoc Testing**: Unscripted exploratory testing to discover edge cases and unexpected behaviors
---

## 7. Test Cases
- Test cases will be documented with unique IDs (TC-001, TC-002, etc.)
- Each test case will reference specific requirements (REQ-xxx)
- Links to detailed test cases: [Analytics Service Test Cases](./test_cases_analytics_service.md)


---

## 8.Roles and Responsibilities
|Name              | Role         | Responsibility                               |
|Georgii Vladimirov| QA           |Execute test cases from p.6                   |

---
## 9. Timeline or Estimation
- **Unit Testing**: 2 Hours
- **Kafka Consumer Testing**: 3 Hours
- **MongoDB Integration Testing**: 2 Hours
- **Event Processing Testing**: 3 Hours
- **Exploratory Testing**: 1.5 Hours
- **Ad-hoc Testing**: 1 Hour
- **Smoke Testing**: 30 min
- **Regression Testing**: 1.5 Hours

- **Total Estimated Time**: 14.5 Hours

---
## 10. Risks and Mitigations
| Risk Description                                   | Likelihood | Impact | Mitigation Strategy                              |
|---------------------------------------------------|------------|--------|--------------------------------------------------|
| Kafka consumer lag or failure                      | High       | High   | Monitor consumer group lag and implement retries |
| MongoDB connection issues                          | Medium     | High   | Verify MongoDB connectivity and authentication   |
| Event message format changes                       | Medium     | High   | Implement schema validation and versioning       |
| Service downtime during tests                      | Low        | High   | Use Docker Compose to manage service lifecycle   |
| Kafka topic unavailability                        | Medium     | High   | Ensure topics are pre-created and accessible     |
| Event processing delays                            | Medium     | Medium | Monitor processing time and implement timeouts   |
| MongoDB storage capacity issues                    | Low        | Medium | Monitor disk usage and implement data retention  |
| Duplicate event processing                         | Medium     | Medium | Implement idempotency checks and deduplication   |
---
## 11. Test Coverage Policy

- Each functional requirement (REQ-xxx) must be covered by at least one test case
- Negative and edge cases are required for critical functionality
- Coverage is tracked via traceability matrix
---
## 12.References to test docs
- [Test Strategy](../docs/test_stategy.md)
- [Requirements Specification](../docs/requirements.md)
---