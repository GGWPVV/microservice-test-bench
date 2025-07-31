# Test plan 
---


## 1.Component: Discount service
_Version: 1.0 | Last updated: 2025-07-31 | Author: Georgii Vladimirov
---

## 2.Date of testing
from 2025-07-31 to 2025-08-02
---
## 3. Testing Environment
- **Environment**: Docker Compose setup including only the required dependencies: user_service, score-service, PostgreSQL, Kafka, Kafdrop, Elasticsearch, Filebeat, Kibana,Redis.
- **Note**: Other services (e.g., analitycs_service) are not required for testing user_service independently
- **Config location**: See `docker-compose.yaml` in the root directory

---
## 4. Entry Testing Criteria
- All services from **Environment** are up and running
- User service is built and deployed
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
---

## 7. Test Cases
- Test cases will be documented with unique IDs (TC-001, TC-002, etc.)
- Each test case will reference specific requirements (REQ-xxx)
- Links to detailed test cases: [User Service Test Cases](./test_cases_discount_service.md)


---

## 8.Roles and Responsibilities
|Name              | Role         | Responsibility                               |
|Georgii Vladimirov| QA           |Execute test cases from p.6                   |

---
## 9. Timeline or Estimation
- **Unit Testing**: 2 Hours
- **API Testing**: 2 Hours
- **Integration Testing**: 1 Hours
- **Exploratory Testing**: 1 Hours 
- **Smoke Testing**: 30 min
- **Regression Testing**: 1 Hours

- **Total Estimated Time**: 7.5 Hours

---
## 10. Risks and Mitigations
| Risk Description                                   | Likelihood | Impact | Mitigation Strategy                              |
|---------------------------------------------------|------------|--------|--------------------------------------------------|
| Kafka topic delays or consumer failure             | Medium     | High   | Ensure Kafka topics are pre-created and monitored |
| Service downtime during tests                      | Low        | High   | Use Docker Compose to manage service lifecycle    |
| Elasticsearch/Filebeat not receiving logs         | Medium     | Medium | Check volume mounts and Filebeat configuration    |
| Test data inconsistencies                          | Medium     | Medium | Use consistent test data setup scripts            |
| Redis cache malfunction                           | Low        | Medium | Verify Redis connectivity and cache operations    |
| Database connection issues                        | Low        | High   | Monitor PostgreSQL health and connection pools    |
| Environment setup failures                        | Medium     | High   | Provide detailed setup documentation and scripts  |
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