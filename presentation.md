---
title: Who Should Design LDE?
author: Sergii Pogorielov
theme: default
paginate: true
marp: true
---

# "Who Should Design LDE (Local Development Environment)?" **Work in Progres**

Sergii Pogorielov

---

# Why Does the LDE Matter?

**Efficiency**: A well-designed LDE reduces friction, enabling developers to focus on writing code rather than troubleshooting setup issues.

**Reproducibility**: Standardized environments ensure consistency between local, staging, and production systems, reducing "it works on my machine" problems.

**Developer Experience (DX)**: An intuitive LDE can significantly impact morale, productivity, and onboarding time for new team members.

---

# Let's ask the internet.

 "Who should use LDE and who should use cloud dev env?" 

 Can we rely on global mind for this answer, yes?

 ---

# Who should use LDE and who should use cloud dev env?

- **Local Development Environment (LDE)**:
  - Individual developers working on isolated tasks.
  - Projects requiring offline access.
  - Development requiring high performance and low latency.

- **Cloud Development Environment**:
  - Teams collaborating on shared codebases.
  - Projects needing scalable resources.
  - Environments requiring easy access from multiple locations.

---

# What?

A developer’s laptop today has performance comparable to or exceeding a 20-year-old supercomputer in areas like CPU, GPU, and memory speed. ... and I can use it only for working on isolated tasks

Sort of like "I have a supercompure but I should use it only as remote terminal becouse I need scalable resources"

---

# Let’s try to design LDE that will be good enough

---

# Typical Web Project stucture

* Applications
    + Frontend ReactJS 
    + Backend Django
    + Backend micro services - FastAPI|NodeJS
    + Lambda Functions

---
# What do we need to fly with all this ?

* Infrastructure:
	+ Database: PostgreSQL, MongoDB
	+ Cache: Redis
	+ Queue: Kafka
* Observability:
	+ Logs
	+ Metrics
	+ Distributed tracing
* Single Sign-On (SSO) service for authentication and authorization across multiple applications

