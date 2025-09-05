# Microservice Test Bench - Data Pipeline Experiments

This project is a **microservices-based application** created as a **learning platform** to practice:

- **Software testing** (manual & automated)
- **Architecture design**
- **Modern development and integration tools**

It simulates a **production-like system** with multiple services, each using its own database and integrated with widely used enterprise technologies.

All testing documentation is available in the [Documentation](#documentation) section.
---

## 🎯 Project Overview

This project implements a **gamified scoring system** demonstrating event-driven microservices architecture:

1. **User Registration** → User Service saves to PostgreSQL → Events to Kafka & ELK
2. **User Login** → JWT authentication → Events to Kafka & ELK  
3. **Score Generation** → Score Service saves to PostgreSQL → Events to Kafka & ELK → Top 10 cached in Redis
4. **Discount Calculation** → Based on age + leaderboard → Cached in Redis → Events to Kafka & ELK
5. **Analytics** → Analytics Service consumes Kafka events → Stores in MongoDB

**Key Technologies:** FastAPI, PostgreSQL, MongoDB, Redis, Kafka, ELK Stack, Docker


## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │    │  Score Service  │    │Discount Service │
│   (FastAPI)     │    │   (FastAPI)     │    │   (FastAPI)     │
│   PostgreSQL    │    │   PostgreSQL    │    │     Redis       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Kafka       │
                    │   (Events)      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │Analytics Service│
                    │   (FastAPI)     │
                    │    MongoDB      │
                    └─────────────────┘
```

## Quick Start

### Prerequisites
- Docker Desktop
- Git

### 1. Clone Repository
```bash
git clone https://github.com/GGWPVV/microservice-test-bench.git
```

### 2. Start All Services
```bash
docker-compose up -d
```

### 3. Access Services
- **APIs**: http://localhost:8000/docs (User), http://localhost:8003/docs (Score), http://localhost:8002/docs (Discount)
- **Kafka UI**: http://localhost:9000
- **Kibana**: http://localhost:5601

##  Monitoring

- **Logs**: Kibana (http://localhost:5601)
- **Events**: Kafdrop (http://localhost:9000)
- **Health**: `/health` endpoints on all services

##  Testing

```bash
cd tests/
pytest user_service/unit_tests/
pytest score_service/integration_tests/
```

See [docs/test_strategy.md](docs/test_strategy.md) for details.

##  Documentation

- [Requirements Specification](docs/requirements.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Test Strategy](docs/test_strategy.md)
- [Test Documentation](tests)
- [Requirements Traceability Matrix](https://www.notion.so/25e317ee517d806fb731c16fb6f0ac5d?v=25e317ee517d80f8a008000c4f15e1a6&source=copy_link)
- [Tests examples from TMS Qase](./tests/Tests%20from%20Qase%20TMS/)
##  License

This project is for educational and demonstration purposes.

---

**Built with for learning microservices architecture**